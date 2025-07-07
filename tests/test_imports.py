#!/usr/bin/env python3
"""Test PyQt5 stubs and basic imports"""

import pytest
import sys
import os

def test_pyqt5_basic_imports():
    """Test that basic PyQt5 imports work with stubs"""
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
        from PyQt5.QtCore import QObject, pyqtSignal
        from PyQt5.QtGui import QColor
        
        # Test creating basic instances
        app = QApplication([])
        assert app is not None
        
        color = QColor(255, 0, 0)
        assert color is not None
        
        # Test QMessageBox static methods exist
        assert hasattr(QMessageBox, 'information')
        assert hasattr(QMessageBox, 'warning')
        assert hasattr(QMessageBox, 'critical')
        
    except ImportError as e:
        pytest.fail(f"PyQt5 import failed: {e}")

def test_qt_constants():
    """Test that Qt constants are available"""
    try:
        from PyQt5.QtCore import Qt
        
        # Test some common constants
        assert hasattr(Qt, 'SolidLine')
        assert hasattr(Qt, 'LeftButton')
        assert hasattr(Qt, 'Key_Escape')
        
    except ImportError as e:
        pytest.fail(f"Qt constants import failed: {e}")

def test_basic_node_imports():
    """Test that basic ReNode classes can be imported"""
    try:
        from ReNode.app import utils
        # Test passed if no import error
        assert utils is not None
        
    except ImportError as e:
        pytest.skip(f"ReNode utils import failed (expected in CI): {e}")

def test_mock_classes():
    """Test mock classes for testing"""
    try:
        from tests.test_mocks import MockNodeFactory, MockApplication, MockCodeGenerator
        
        factory = MockNodeFactory()
        assert factory is not None
        assert hasattr(factory, 'getNodeLibData')
        
        app = MockApplication()
        assert app is not None
        assert hasattr(app, 'args')
        
        codegen = MockCodeGenerator()
        assert codegen is not None
        assert hasattr(codegen, 'generateProcess')
        
    except ImportError as e:
        pytest.fail(f"Mock classes import failed: {e}")

def test_python_version():
    """Test Python version is 3.12+"""
    assert sys.version_info >= (3, 12), f"Python 3.12+ required, got {sys.version_info}"

def test_basic_modules():
    """Test basic Python modules are available"""
    import json
    import re
    import os
    import tempfile
    
    # Test they work
    data = json.dumps({"test": True})
    assert json.loads(data)["test"] is True
    
    match = re.search(r'test', 'testing')
    assert match is not None
    
    assert os.path.exists('.')
    
    with tempfile.NamedTemporaryFile() as f:
        assert f.name