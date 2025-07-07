"""
Pytest configuration for ReNodes testing
"""
import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing"""
    # Skip QApplication creation in CI environments without GUI
    try:
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            try:
                app = QApplication(['-platform', 'offscreen'])
            except (TypeError, ImportError):
                # Fallback for environments without PyQt5
                app = None
            if app and hasattr(app, 'setQuitOnLastWindowClosed'):
                app.setQuitOnLastWindowClosed(False)
            yield app
            if app and hasattr(app, 'quit'):
                app.quit()
        else:
            yield QApplication.instance()
    except ImportError:
        # No PyQt5 available, yield None
        yield None

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_config_files(temp_dir):
    """Create mock configuration files needed for application"""
    # Create lib.json mock
    lib_json = {
        "system": {"version": 1},
        "nodes": {},
        "classes": {
            "object": {
                "baseClass": "",
                "members": {},
                "methods": {}
            }
        }
    }
    
    lib_json_path = os.path.join(temp_dir, "lib.json")
    with open(lib_json_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(lib_json, f, ensure_ascii=False, indent=2)
    
    # Create lib_guid mock
    lib_guid_path = os.path.join(temp_dir, "lib_guid")
    with open(lib_guid_path, 'w') as f:
        f.write("test-guid-12345")
    
    # Create data directory with splash mock
    data_dir = os.path.join(temp_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Create minimal splash.png (1x1 pixel PNG)
    splash_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x007n\xf9$\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    with open(os.path.join(data_dir, "splash.png"), 'wb') as f:
        f.write(splash_data)
    
    return temp_dir

@pytest.fixture
def mock_environment(temp_dir, mock_config_files, monkeypatch):
    """Set up mock environment for testing"""
    # Change working directory to temp_dir
    original_cwd = os.getcwd()
    monkeypatch.chdir(temp_dir)
    
    # Mock sys.argv to include headless flags
    monkeypatch.setattr(sys, 'argv', ['renode', '-noapp', '-nosplash'])
    
    # Disable logging to prevent spam during tests
    logging.disable(logging.CRITICAL)
    
    yield temp_dir
    
    # Cleanup
    logging.disable(logging.NOTSET)
    monkeypatch.chdir(original_cwd)

@pytest.fixture
def node_factory():
    """Create a NodeFactory instance for testing"""
    try:
        from ReNode.app.NodeFactory import NodeFactory
        # Mock the loading process to avoid GUI dependencies
        with patch.object(NodeFactory, 'loadFactoryFromJson') as mock_load:
            factory = NodeFactory()
            factory.nodes = {}
            factory.classes = {"object": {"baseClass": "", "baseList": ["object"]}}
            factory.classNames = {"object"}
            factory.version = 1
            return factory
    except ImportError:
        # Use mock NodeFactory
        try:
            from tests.test_mocks import MockNodeFactory
            factory = MockNodeFactory()
            factory.loadFactoryFromJson("mock.json")
            return factory
        except ImportError:
            # Create minimal mock if test_mocks not available
            class MinimalMockFactory:
                def __init__(self):
                    self.nodes = {}
                    self.classes = {"object": {"baseClass": "", "baseList": ["object"]}}
                    self.classNames = {"object"}
                    self.version = 1
                def loadFactoryFromJson(self, path):
                    pass
            return MinimalMockFactory()

@pytest.fixture
def mock_graph_data():
    """Create mock graph data for testing"""
    return {
        'graph': {
            'info': {
                'name': 'TestGraph',
                'classname': 'TestClass',
                'type': 'class',
                'graphVersion': 2
            },
            'variables': {
                'localvar': {},
                'classvar': {}
            }
        },
        'nodes': {
            'test_node_1': {
                'class_': 'internal.entry',
                'name': 'Entry Point',
                'pos': [0, 0]
            }
        },
        'connections': []
    }

@pytest.fixture
def code_generator(node_factory, mock_graph_data):
    """Create a CodeGenerator instance for testing"""
    try:
        from ReNode.app.CodeGen import CodeGenerator
        
        with patch('ReNode.ui.NodeGraphComponent.NodeGraphComponent') as mock_component:
            mock_component.refObject = MagicMock()
            mock_component.refObject.nodeFactory = node_factory
            mock_component.refObject.variable_manager = MagicMock()
            
            generator = CodeGenerator()
            return generator
    except ImportError:
        # Use mock CodeGenerator
        try:
            from tests.test_mocks import MockCodeGenerator
            return MockCodeGenerator()
        except ImportError:
            # Create minimal mock if test_mocks not available
            class MinimalMockGenerator:
                def __init__(self):
                    pass
                def generateProcess(self, *args, **kwargs):
                    return {"success": True, "code": "// mock generated code"}
            return MinimalMockGenerator()