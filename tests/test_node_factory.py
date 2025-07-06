"""
Tests for NodeFactory component
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from ReNode.app.NodeFactory import NodeFactory


class TestNodeFactory:
    """Test cases for NodeFactory"""
    
    def test_init(self, mock_environment):
        """Test NodeFactory initialization"""
        with patch.object(NodeFactory, 'loadFactoryFromJson'):
            factory = NodeFactory()
            assert factory is not None
            assert hasattr(factory, 'nodes')
            assert hasattr(factory, 'classes')
            assert hasattr(factory, 'version')
    
    def test_register_simple_node(self, node_factory):
        """Test registering a simple node"""
        node_data = {
            'name': 'Test Node',
            'desc': 'Test description',
            'inputs': {
                'input1': {'type': 'int', 'desc': 'Test input'}
            },
            'outputs': {
                'output1': {'type': 'string', 'desc': 'Test output'}
            }
        }
        
        node_factory.registerNodeInLib('test', 'simple_node', node_data)
        
        assert 'test.simple_node' in node_factory.nodes
        registered_node = node_factory.nodes['test.simple_node']
        assert registered_node['name'] == 'Test Node'
        assert registered_node['desc'] == 'Test description'
        assert 'input1' in registered_node['inputs']
        assert 'output1' in registered_node['outputs']
    
    def test_deserialize_connectors_input(self, node_factory):
        """Test deserializing input connectors"""
        inputs = {
            'test_input': {
                'type': 'int',
                'desc': 'Test input port',
                'default_value': 42
            }
        }
        
        result = node_factory._deserializeConnectors(inputs, True)
        
        assert 'test_input' in result
        connector = result['test_input']
        assert connector['type'] == 'int'
        assert connector['desc'] == 'Test input port'
        assert connector['default_value'] == 42
        assert connector['require_connection'] == True
    
    def test_deserialize_connectors_output(self, node_factory):
        """Test deserializing output connectors"""
        outputs = {
            'test_output': {
                'type': 'string',
                'mutliconnect': True
            }
        }
        
        result = node_factory._deserializeConnectors(outputs, False)
        
        assert 'test_output' in result
        connector = result['test_output']
        assert connector['type'] == 'string'
        assert connector['mutliconnect'] == True
        assert 'accepted_paths' in connector
    
    def test_get_color_by_type(self, node_factory):
        """Test getting color by type"""
        # Mock variable manager
        with patch('ReNode.ui.NodeGraphComponent.NodeGraphComponent') as mock_component:
            mock_var_mgr = MagicMock()
            mock_var_mgr.variableTempateData = []
            mock_component.refObject.variable_manager = mock_var_mgr
            
            # Test default color
            color = node_factory.getColorByType('unknown_type')
            assert color == NodeFactory.defaultColor
    
    def test_decompose_type(self, node_factory):
        """Test type decomposition"""
        # Test array type
        result = node_factory.decomposeType('array[int]')
        assert result[0] == 'array'
        assert result[1] == 'int'
        
        # Test function type
        result = node_factory.decomposeType('function[void,int,string]')
        assert result[0] == 'function'
        assert result[1] == 'void'
    
    def test_compose_type(self, node_factory):
        """Test type composition"""
        result = node_factory.composeType(['array', 'int'])
        assert result == 'array[int]'
        
        result = node_factory.composeType(['function', 'void', 'int', 'string'])
        assert result == 'function[void,int,string]'
    
    def test_class_hierarchy(self, node_factory):
        """Test class hierarchy methods"""
        # Add test classes
        node_factory.classes = {
            'object': {'baseClass': '', 'baseList': ['object']},
            'GameObject': {'baseClass': 'object', 'baseList': ['GameObject', 'object']},
            'Item': {'baseClass': 'GameObject', 'baseList': ['Item', 'GameObject', 'object']}
        }
        
        # Test getting all parents
        parents = node_factory.getClassAllParents('Item')
        assert 'Item' in parents
        assert 'GameObject' in parents
        assert 'object' in parents
        
        # Test type checking
        assert node_factory.isTypeOf('Item', 'GameObject') == True
        assert node_factory.isTypeOf('Item', 'object') == True
        assert node_factory.isTypeOf('GameObject', 'Item') == False
    
    def test_inheritance_process(self, node_factory):
        """Test inheritance processing"""
        test_classes = {
            'object': {'baseClass': ''},
            'BaseClass': {'baseClass': 'object'},
            'ChildClass': {'baseClass': 'BaseClass'}
        }
        
        node_factory.inheritanceProcess(test_classes)
        
        assert test_classes['object']['baseList'] == ['object']
        assert test_classes['BaseClass']['baseList'] == ['BaseClass', 'object']
        assert test_classes['ChildClass']['baseList'] == ['ChildClass', 'BaseClass', 'object']


class TestNodeFactoryIntegration:
    """Integration tests for NodeFactory"""
    
    def test_load_empty_library(self, mock_environment):
        """Test loading empty library"""
        empty_lib = {
            "system": {"version": 1},
            "nodes": {},
            "classes": {"object": {"baseClass": ""}}
        }
        
        with open('test_lib.json', 'w', encoding='utf-8') as f:
            json.dump(empty_lib, f)
        
        factory = NodeFactory()
        # Mock VirtualLib to avoid GUI dependencies
        with patch.object(factory, 'vlib'):
            factory.loadFactoryFromJson('test_lib.json')
        
        assert factory.version == 1
        assert 'object' in factory.classes
    
    def test_deserialize_complete_library(self, mock_environment):
        """Test deserializing a complete library"""
        complete_lib = {
            "system": {"version": 2},
            "nodes": {
                "math": {
                    "add": {
                        "name": "Add",
                        "desc": "Add two numbers",
                        "inputs": {
                            "a": {"type": "int"},
                            "b": {"type": "int"}
                        },
                        "outputs": {
                            "result": {"type": "int"}
                        },
                        "code": "@genvar.out.1 = @in.1 + @in.2"
                    }
                }
            },
            "classes": {
                "object": {"baseClass": ""},
                "GameObject": {"baseClass": "object"}
            }
        }
        
        with open('complete_lib.json', 'w', encoding='utf-8') as f:
            json.dump(complete_lib, f)
        
        factory = NodeFactory()
        with patch.object(factory, 'vlib'):
            factory.loadFactoryFromJson('complete_lib.json')
        
        assert factory.version == 2
        assert 'math.add' in factory.nodes
        assert 'GameObject' in factory.classes
        
        add_node = factory.nodes['math.add']
        assert add_node['name'] == 'Add'
        assert add_node['code'] == "@genvar.out.1 = @in.1 + @in.2"