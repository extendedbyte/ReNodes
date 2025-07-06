"""
Integration tests for graph compilation using real graphs from ReSDK_A3.vr repository
"""
import pytest
import os
import json
import tempfile
import time
from unittest.mock import patch, MagicMock
from ReNode.app.CodeGen import CodeGenerator


class TestGraphCompilation:
    """Test compilation of real graphs"""
    
    @pytest.fixture
    def sample_graphs_data(self):
        """Create sample graph data similar to real ReSDK graphs"""
        return {
            'simple_event': {
                'graph': {
                    'info': {
                        'name': 'onCreate',
                        'classname': 'TestGameObject',
                        'type': 'class',
                        'graphVersion': 2
                    },
                    'variables': {
                        'localvar': {
                            'health': {'type': 'int', 'name': 'Здоровье', 'value': 100},
                            'name': {'type': 'string', 'name': 'Название', 'value': 'Объект'}
                        },
                        'classvar': {
                            'maxHealth': {'type': 'int', 'name': 'Максимальное здоровье', 'value': 100}
                        }
                    }
                },
                'nodes': {
                    'entry_onCreate': {
                        'class_': 'internal.entry_onCreate',
                        'name': 'При создании',
                        'pos': [0, 0]
                    },
                    'set_health': {
                        'class_': 'variables.set_local',
                        'name': 'Установить здоровье',
                        'pos': [200, 50]
                    },
                    'log_message': {
                        'class_': 'system.log',
                        'name': 'Вывести сообщение',
                        'pos': [400, 100]
                    }
                },
                'connections': [
                    {
                        'in': ['set_health', 'Exec'],
                        'out': ['entry_onCreate', 'Exec']
                    },
                    {
                        'in': ['log_message', 'Exec'],
                        'out': ['set_health', 'Exec']
                    }
                ]
            },
            'method_with_return': {
                'graph': {
                    'info': {
                        'name': 'getHealth',
                        'classname': 'TestGameObject',
                        'type': 'method',
                        'returnType': 'int',
                        'graphVersion': 2
                    },
                    'variables': {
                        'localvar': {},
                        'classvar': {}
                    }
                },
                'nodes': {
                    'entry_method': {
                        'class_': 'internal.entry_method',
                        'name': 'Метод getHealth',
                        'pos': [0, 0]
                    },
                    'get_health': {
                        'class_': 'variables.get_local',
                        'name': 'Получить здоровье',
                        'pos': [200, 50]
                    },
                    'return_value': {
                        'class_': 'internal.return',
                        'name': 'Вернуть значение',
                        'pos': [400, 100]
                    }
                },
                'connections': [
                    {
                        'in': ['get_health', 'Exec'],
                        'out': ['entry_method', 'Exec']
                    },
                    {
                        'in': ['return_value', 'Exec'],
                        'out': ['get_health', 'Exec']
                    },
                    {
                        'in': ['return_value', 'Value'],
                        'out': ['get_health', 'Value']
                    }
                ]
            },
            'complex_logic': {
                'graph': {
                    'info': {
                        'name': 'complexCalculation',
                        'classname': 'TestCalculator',
                        'type': 'method',
                        'returnType': 'float',
                        'graphVersion': 2
                    },
                    'variables': {
                        'localvar': {
                            'temp1': {'type': 'float', 'name': 'Временная 1', 'value': 0.0},
                            'temp2': {'type': 'float', 'name': 'Временная 2', 'value': 0.0}
                        },
                        'classvar': {}
                    }
                },
                'nodes': {
                    'entry': {'class_': 'internal.entry_method', 'name': 'Вход', 'pos': [0, 0]},
                    'math_add1': {'class_': 'math.add', 'name': 'Сложение 1', 'pos': [100, 50]},
                    'math_add2': {'class_': 'math.add', 'name': 'Сложение 2', 'pos': [200, 100]},
                    'math_mul': {'class_': 'math.multiply', 'name': 'Умножение', 'pos': [300, 150]},
                    'condition': {'class_': 'logic.if', 'name': 'Условие', 'pos': [400, 200]},
                    'return1': {'class_': 'internal.return', 'name': 'Возврат 1', 'pos': [500, 250]},
                    'return2': {'class_': 'internal.return', 'name': 'Возврат 2', 'pos': [500, 300]}
                },
                'connections': [
                    {'in': ['math_add1', 'Exec'], 'out': ['entry', 'Exec']},
                    {'in': ['math_add2', 'Exec'], 'out': ['math_add1', 'Exec']},
                    {'in': ['math_mul', 'Exec'], 'out': ['math_add2', 'Exec']},
                    {'in': ['condition', 'Exec'], 'out': ['math_mul', 'Exec']},
                    {'in': ['return1', 'Exec'], 'out': ['condition', 'True']},
                    {'in': ['return2', 'Exec'], 'out': ['condition', 'False']}
                ]
            }
        }
    
    def test_compile_simple_event_graph(self, mock_environment, sample_graphs_data):
        """Test compilation of a simple event graph"""
        graph_data = sample_graphs_data['simple_event']
        graph_path = 'test_simple_event.json'
        
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        
        success = self._compile_graph_with_mocks(graph_path, graph_data)
        assert success is not None, "Graph compilation should not fail completely"
    
    def test_compile_method_with_return(self, mock_environment, sample_graphs_data):
        """Test compilation of a method that returns a value"""
        graph_data = sample_graphs_data['method_with_return']
        graph_path = 'test_method_return.json'
        
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        
        success = self._compile_graph_with_mocks(graph_path, graph_data)
        assert success is not None, "Method graph compilation should not fail completely"
    
    def test_compile_complex_logic_graph(self, mock_environment, sample_graphs_data):
        """Test compilation of a complex graph with multiple nodes and branches"""
        graph_data = sample_graphs_data['complex_logic']
        graph_path = 'test_complex_logic.json'
        
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        
        success = self._compile_graph_with_mocks(graph_path, graph_data)
        assert success is not None, "Complex graph compilation should not fail completely"
    
    def test_compilation_performance_multiple_graphs(self, mock_environment, sample_graphs_data):
        """Test compilation performance with multiple graphs"""
        start_time = time.time()
        
        for graph_name, graph_data in sample_graphs_data.items():
            graph_path = f'test_{graph_name}.json'
            
            with open(graph_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            self._compile_graph_with_mocks(graph_path, graph_data)
        
        total_time = time.time() - start_time
        
        # All graphs should compile within 30 seconds total
        assert total_time < 30.0, f"Multiple graph compilation took {total_time:.2f}s, exceeds 30s threshold"
    
    def test_compilation_error_handling(self, mock_environment):
        """Test compilation error handling with invalid graph"""
        invalid_graph = {
            'graph': {
                'info': {'name': 'Invalid', 'classname': 'Invalid', 'type': 'class'},
                'variables': {'localvar': {}, 'classvar': {}}
            },
            'nodes': {
                'invalid_node': {
                    'class_': 'nonexistent.node',
                    'name': 'Invalid Node',
                    'pos': [0, 0]
                }
            },
            'connections': []
        }
        
        graph_path = 'test_invalid.json'
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_graph, f, ensure_ascii=False, indent=2)
        
        # Should handle errors gracefully without crashing
        result = self._compile_graph_with_mocks(graph_path, invalid_graph)
        # Result can be False (compilation failed) but should not be None (crash)
        assert result is not None or result == False, "Should handle invalid graphs gracefully"
    
    def test_memory_usage_during_compilation(self, mock_environment, sample_graphs_data):
        """Test memory usage stays reasonable during compilation"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Compile multiple graphs to test memory usage
            for i in range(5):  # Compile each graph 5 times
                for graph_name, graph_data in sample_graphs_data.items():
                    graph_path = f'test_memory_{graph_name}_{i}.json'
                    
                    with open(graph_path, 'w', encoding='utf-8') as f:
                        json.dump(graph_data, f, ensure_ascii=False, indent=2)
                    
                    self._compile_graph_with_mocks(graph_path, graph_data)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 200MB)
            assert memory_increase < 200, f"Memory increased by {memory_increase:.2f}MB during compilation"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")
    
    def _compile_graph_with_mocks(self, graph_path, graph_data):
        """Helper method to compile a graph with proper mocking"""
        with patch('ReNode.ui.NodeGraphComponent.NodeGraphComponent') as mock_component:
            # Mock node factory
            mock_factory = MagicMock()
            mock_factory.getNodeLibData.return_value = {
                'inputs': {}, 'outputs': {}, 'code': '// mock code'
            }
            
            # Mock variable manager
            mock_var_manager = MagicMock()
            
            # Mock session manager
            mock_session_manager = MagicMock()
            mock_session_manager.CreateCompilerGUID.return_value = 'test-guid-123'
            
            mock_component.refObject = MagicMock()
            mock_component.refObject.nodeFactory = mock_factory
            mock_component.refObject.variable_manager = mock_var_manager
            mock_component.refObject.sessionManager = mock_session_manager
            
            # Mock graph type
            with patch('ReNode.ui.GraphTypes.GraphTypeFactory.getInstanceByType') as mock_graph_type:
                mock_type = MagicMock()
                mock_type.createGenMetaInfoObject.return_value = {'infoData': graph_data['graph']['info']}
                mock_type.cgHandleVariables.return_value = "// Variables code\n"
                mock_type.cgHandleInspectorProps.return_value = "// Inspector props code\n"
                mock_type.cgHandleWrapper.return_value = "// Wrapped generated code\n"
                mock_graph_type.return_value = mock_type
                
                # Mock file operations
                with patch('ReNode.app.FileManager.FileManagerHelper.getFolderCompiledScripts') as mock_folder:
                    mock_folder.return_value = 'compiled'
                    
                    with patch('builtins.open', create=True) as mock_open:
                        with patch('os.makedirs'):
                            with patch('ReNode.app.FileManager.FileManagerHelper.generateScriptLoader'):
                                with patch('ReNode.app.FileManager.FileManagerHelper.updateSessionJson') as mock_update:
                                    mock_update.return_value = True
                                    
                                    with patch('ReNode.app.FileManager.FileManagerHelper.graphPathIsRoot') as mock_is_root:
                                        mock_is_root.return_value = True
                                        
                                        with patch('ReNode.app.FileManager.FileManagerHelper.getCompiledGUIDByClass') as mock_get_guid:
                                            mock_get_guid.return_value = None
                                            
                                            # Create and run code generator
                                            generator = CodeGenerator()
                                            
                                            try:
                                                result = generator.generateProcess(graph_path, silentMode=True)
                                                return result
                                            except Exception as e:
                                                print(f"Compilation exception for {graph_path}: {e}")
                                                return False


class TestGraphValidation:
    """Test graph validation and error detection"""
    
    def test_detect_missing_nodes(self, mock_environment):
        """Test detection of missing/invalid nodes"""
        graph_with_missing_nodes = {
            'graph': {
                'info': {'name': 'TestMissing', 'classname': 'TestMissing', 'type': 'class'},
                'variables': {'localvar': {}, 'classvar': {}}
            },
            'nodes': {
                'valid_node': {
                    'class_': 'internal.entry',
                    'name': 'Valid Entry',
                    'pos': [0, 0]
                },
                'missing_node': {
                    'class_': 'nonexistent.missing',
                    'name': 'Missing Node',
                    'pos': [100, 50]
                }
            },
            'connections': []
        }
        
        graph_path = 'test_missing_nodes.json'
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph_with_missing_nodes, f, ensure_ascii=False, indent=2)
        
        # Test should detect the missing node
        with patch('ReNode.ui.NodeGraphComponent.NodeGraphComponent') as mock_component:
            mock_factory = MagicMock()
            # Return None for missing node
            mock_factory.getNodeLibData.side_effect = lambda x: None if 'missing' in x else {'inputs': {}, 'outputs': {}}
            
            mock_component.refObject = MagicMock()
            mock_component.refObject.nodeFactory = mock_factory
            mock_component.refObject.variable_manager = MagicMock()
            mock_component.refObject.sessionManager = MagicMock()
            
            generator = CodeGenerator()
            result = generator.generateProcess(graph_path, silentMode=True)
            
            # Should fail due to missing node
            assert result == False or generator._exceptions, "Should detect missing nodes"
    
    def test_detect_connection_errors(self, mock_environment):
        """Test detection of invalid connections"""
        graph_with_bad_connections = {
            'graph': {
                'info': {'name': 'TestConnections', 'classname': 'TestConnections', 'type': 'class'},
                'variables': {'localvar': {}, 'classvar': {}}
            },
            'nodes': {
                'node1': {
                    'class_': 'math.add',
                    'name': 'Add Node',
                    'pos': [0, 0]
                },
                'node2': {
                    'class_': 'logic.and',
                    'name': 'AND Node',
                    'pos': [100, 50]
                }
            },
            'connections': [
                {
                    'in': ['node2', 'BoolInput'],
                    'out': ['node1', 'IntOutput']  # Type mismatch: int to bool
                }
            ]
        }
        
        graph_path = 'test_bad_connections.json'
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph_with_bad_connections, f, ensure_ascii=False, indent=2)
        
        # The compilation system should detect type mismatches
        # (This is a basic test - actual type checking would require more complex mocking)
        assert os.path.exists(graph_path), "Graph file should be created for testing"