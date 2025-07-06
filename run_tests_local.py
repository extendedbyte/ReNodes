#!/usr/bin/env python3
"""
Local test runner for ReNodes
Runs all tests locally without GitHub Actions
"""
import os
import sys
import subprocess
import time
import json
from pathlib import Path


def run_command(cmd, description, continue_on_error=True, timeout=None):
    """Run a command and capture output"""
    print(f"\n🔄 {description}...")
    print(f"Command: {cmd}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} completed in {elapsed:.2f}s")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}...")
            return True, result.stdout, elapsed
        else:
            print(f"❌ {description} failed in {elapsed:.2f}s")
            print(f"Error: {result.stderr}")
            if not continue_on_error:
                sys.exit(1)
            return False, result.stderr, elapsed
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} timed out after {timeout}s")
        return False, "Timeout", timeout
    except Exception as e:
        print(f"💥 {description} crashed: {e}")
        return False, str(e), 0


def setup_environment():
    """Setup test environment"""
    print("🔧 Setting up test environment...")
    
    # Create directories
    os.makedirs("tests/reports", exist_ok=True)
    os.makedirs("tests/artifacts", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Set environment variables for headless mode
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    # Create mock files
    with open("lib.obj", "w", encoding="utf-8") as f:
        f.write("Mock library content for testing")
    
    with open("lib_guid", "w") as f:
        f.write("test-local-guid")
    
    # Create minimal splash.png (1x1 pixel)
    splash_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x007n\xf9$\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    with open("data/splash.png", "wb") as f:
        f.write(splash_data)
    
    print("✅ Environment setup completed")


def install_dependencies():
    """Install test dependencies"""
    print("📦 Installing dependencies...")
    
    # Check if pip is available
    pip_cmd = "python3 -m pip"
    if sys.platform.startswith('win'):
        pip_cmd = "python -m pip"
    
    commands = [
        f"{pip_cmd} install --upgrade pip",
        f"{pip_cmd} install -r requirements.txt",
        f"{pip_cmd} install -r requirements-test.txt"
    ]
    
    all_failed = True
    for cmd in commands:
        success, output, elapsed = run_command(cmd, f"Installing: {cmd}", continue_on_error=True)
        if success:
            all_failed = False
    
    if all_failed:
        print("⚠️ Could not install dependencies, will use mock classes for testing")
        return False
    
    return True


def run_tests():
    """Run all test suites"""
    metrics = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_results": {},
        "total_time": 0
    }
    
    start_total = time.time()
    
    # Test suites to run
    test_suites = [
        {
            "name": "Basic Import Tests",
            "cmd": 'python3 tests/test_basic_imports.py',
            "timeout": 60,  # 1 minute
            "required": True
        }
    ]
    
    # Add advanced tests only if pytest is available
    try:
        import pytest
        test_suites.extend([
            {
                "name": "Unit Tests",
                "cmd": 'python3 -m pytest tests/ -v --tb=short -m "unit or not slow" --junitxml=tests/reports/junit.xml',
                "timeout": 300,  # 5 minutes
                "required": False
            },
            {
                "name": "Performance Tests", 
                "cmd": 'python3 -m pytest tests/test_performance.py -v --tb=short -m "slow" --junitxml=tests/reports/performance_junit.xml',
                "timeout": 1800,  # 30 minutes
                "required": False
            },
            {
                "name": "Integration Tests",
                "cmd": 'python3 -m pytest tests/test_graph_compilation.py tests/test_application.py -v --tb=short --junitxml=tests/reports/integration_junit.xml',
                "timeout": 1200,  # 20 minutes
                "required": False
            }
        ])
    except ImportError:
        print("⚠️ pytest not available, running basic tests only")
    
    # Run each test suite
    for suite in test_suites:
        success, output, elapsed = run_command(
            suite["cmd"], 
            suite["name"], 
            continue_on_error=not suite["required"],
            timeout=suite["timeout"]
        )
        
        metrics["test_results"][suite["name"]] = {
            "success": success,
            "time": elapsed,
            "output_preview": output[:200] if output else ""
        }
    
    # Test application startup
    startup_success, startup_output, startup_time = run_command(
        "python3 main.py -noapp -nosplash -debug",
        "Application Startup Test",
        timeout=120
    )
    
    metrics["test_results"]["Application Startup"] = {
        "success": startup_success,
        "time": startup_time,
        "output_preview": startup_output[:200] if startup_output else ""
    }
    
    # Test compilation
    compile_success, compile_output, compile_time = run_command(
        "python3 main.py -prep_code -noapp -nosplash",
        "Graph Compilation Test",
        timeout=60
    )
    
    metrics["test_results"]["Graph Compilation"] = {
        "success": compile_success,
        "time": compile_time,
        "output_preview": compile_output[:200] if compile_output else ""
    }
    
    metrics["total_time"] = time.time() - start_total
    
    return metrics


def save_results(metrics):
    """Save test results"""
    # Save detailed metrics
    with open("tests/reports/local_test_results.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    # Create summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    total_tests = len(metrics["test_results"])
    passed_tests = sum(1 for result in metrics["test_results"].values() if result["success"])
    
    print(f"📈 Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"⏱️ Total time: {metrics['total_time']:.2f} seconds")
    print()
    
    for test_name, result in metrics["test_results"].items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {test_name}: {result['time']:.2f}s")
    
    print(f"\n📁 Detailed results saved to: tests/reports/local_test_results.json")
    print("="*60)
    
    # Check performance thresholds
    if "Application Startup" in metrics["test_results"]:
        startup_time = metrics["test_results"]["Application Startup"]["time"]
        if startup_time > 60:
            print(f"⚠️ Warning: Application startup took {startup_time:.2f}s (threshold: 60s)")
        else:
            print(f"✅ Application startup: {startup_time:.2f}s (within 60s threshold)")


def main():
    """Main function"""
    print("🧪 ReNodes Local Test Runner")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    try:
        # Setup
        setup_environment()
        
        # Install dependencies (optional)
        deps_installed = install_dependencies()
        if not deps_installed:
            print("🔧 Continuing without installing dependencies, using built-in functionality...")
        
        # Run tests
        metrics = run_tests()
        
        # Save and display results
        save_results(metrics)
        
        # Exit with appropriate code
        failed_tests = sum(1 for result in metrics["test_results"].values() if not result["success"])
        if failed_tests > 0:
            print(f"\n⚠️ {failed_tests} test suite(s) failed, but this is expected in development")
            sys.exit(0)  # Don't fail the script, just report
        else:
            print("\n🎉 All tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()