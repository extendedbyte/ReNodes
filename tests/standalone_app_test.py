#!/usr/bin/env python3
"""Standalone application test with PyQt5 stubs - not a pytest test"""

import sys
import os
import time

# Add project root and tests to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and create comprehensive stubs
print("🔧 Setting up PyQt5/Qt stubs...")
import pyqt5_stub_helper
print("✅ PyQt5/Qt stubs configured")

# Now we can import the application
print("🔄 Testing application import...")
try:
    start_time = time.time()
    from ReNode.app.application import AppMain
    elapsed = time.time() - start_time
    print(f"✅ Application imported successfully in {elapsed:.2f}s")
except Exception as e:
    print(f"❌ Failed to import application: {e}")
    raise

# Test basic functionality
print("🔄 Testing application initialization...")
try:
    # Test with headless arguments
    test_args = [sys.argv[0], "-noapp", "-nosplash", "-debug"]
    sys.argv = test_args
    
    # Create app instance
    app = AppMain()
    print("✅ Application instance created")
    
    # Test argument parsing
    if hasattr(app, 'args'):
        print(f"✅ Arguments parsed: noapp={getattr(app.args, 'noapp', False)}, nosplash={getattr(app.args, 'nosplash', False)}")
    
    print("🎉 All application tests passed!")
    
except Exception as e:
    print(f"❌ Application test failed: {e}")
    import traceback
    traceback.print_exc()
    raise