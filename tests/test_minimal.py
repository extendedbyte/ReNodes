"""
Minimal test to ensure testing system works
"""
import sys
import os

def test_python_version():
    """Test that we have a working Python version"""
    assert sys.version_info >= (3, 6), "Python 3.6+ required"
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")

def test_basic_imports():
    """Test basic imports work"""
    import json
    import unittest
    import os
    import sys
    print("✅ Basic imports OK")

def test_unittest_mock():
    """Test that unittest.mock is available (built into Python 3.3+)"""
    from unittest.mock import patch, MagicMock
    mock = MagicMock()
    mock.test_method.return_value = "test"
    assert mock.test_method() == "test"
    print("✅ unittest.mock OK")

def test_file_operations():
    """Test basic file operations"""
    test_file = "test_temp.txt"
    with open(test_file, "w") as f:
        f.write("test content")
    
    assert os.path.exists(test_file)
    
    with open(test_file, "r") as f:
        content = f.read()
    assert content == "test content"
    
    os.remove(test_file)
    print("✅ File operations OK")

if __name__ == "__main__":
    test_python_version()
    test_basic_imports()
    test_unittest_mock()
    test_file_operations()
    print("🎉 All minimal tests passed!")