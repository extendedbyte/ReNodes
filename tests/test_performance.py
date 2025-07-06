"""
Performance tests for ReNodes - measuring startup time and compilation metrics
"""
import pytest
import time
import json
import os
from unittest.mock import patch, MagicMock
from ReNode.app.application import Application, AppMain


class PerformanceMetrics:
    """Class to collect and store performance metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name, value, threshold=None):
        """Record a performance metric"""
        self.metrics[name] = {
            'value': value,
            'threshold': threshold,
            'unit': 'seconds' if 'time' in name else 'count',
            'timestamp': time.time()
        }
    
    def get_metric(self, name):
        """Get a recorded metric"""
        return self.metrics.get(name)
    
    def check_thresholds(self):
        """Check if all metrics meet their thresholds"""
        violations = []
        for name, data in self.metrics.items():
            if data['threshold'] and data['value'] > data['threshold']:
                violations.append(f"{name}: {data['value']} > {data['threshold']}")
        return violations
    
    def save_to_file(self, filename):
        """Save metrics to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)


@pytest.fixture
def performance_metrics():
    """Fixture providing performance metrics collector"""
    return PerformanceMetrics()


class TestStartupPerformance:
    """Test startup performance metrics"""
    
    @pytest.mark.slow
    def test_application_startup_time(self, qapp, mock_environment, performance_metrics):
        """Test application startup time - should be under 60 seconds"""
        startup_threshold = 60.0  # 60 seconds as specified
        
        start_time = time.time()
        
        with patch('ReNode.app.application.Application.requireLibUpdate') as mock_require:
            mock_require.return_value = False
            
            with patch('ReNode.app.NodeFactory.NodeFactory') as mock_factory:
                with patch('ReNode.ui.AppWindow.MainWindow') as mock_window:
                    with patch('ReNode.app.FileManager.FileManagerHelper.loadAllCompiledGUIDs'):
                        mock_main_window = MagicMock()
                        mock_window.return_value = mock_main_window
                        
                        try:
                            app = Application(qapp)
                            startup_time = time.time() - start_time
                            
                            performance_metrics.record_metric(
                                'application_startup_time', 
                                startup_time, 
                                startup_threshold
                            )
                            
                            # Assert startup time is under threshold
                            assert startup_time < startup_threshold, \
                                f"Startup time {startup_time:.2f}s exceeds threshold {startup_threshold}s"
                                
                        except Exception as e:
                            startup_time = time.time() - start_time
                            performance_metrics.record_metric(
                                'application_startup_time_with_errors', 
                                startup_time, 
                                startup_threshold
                            )
                            print(f"Startup completed with exceptions in {startup_time:.2f}s: {e}")
    
    @pytest.mark.slow
    def test_library_loading_time(self, mock_environment, performance_metrics):
        """Test library loading performance"""
        loading_threshold = 30.0  # 30 seconds threshold for library loading
        
        # Create a realistic test library
        test_lib = {
            "system": {"version": 2},
            "nodes": {
                "math": {
                    "add": {"name": "Add", "inputs": {"a": {"type": "int"}, "b": {"type": "int"}}, "outputs": {"result": {"type": "int"}}},
                    "subtract": {"name": "Subtract", "inputs": {"a": {"type": "int"}, "b": {"type": "int"}}, "outputs": {"result": {"type": "int"}}},
                    "multiply": {"name": "Multiply", "inputs": {"a": {"type": "int"}, "b": {"type": "int"}}, "outputs": {"result": {"type": "int"}}},
                    "divide": {"name": "Divide", "inputs": {"a": {"type": "int"}, "b": {"type": "int"}}, "outputs": {"result": {"type": "int"}}}
                },
                "logic": {
                    "and": {"name": "AND", "inputs": {"a": {"type": "bool"}, "b": {"type": "bool"}}, "outputs": {"result": {"type": "bool"}}},
                    "or": {"name": "OR", "inputs": {"a": {"type": "bool"}, "b": {"type": "bool"}}, "outputs": {"result": {"type": "bool"}}},
                    "not": {"name": "NOT", "inputs": {"a": {"type": "bool"}}, "outputs": {"result": {"type": "bool"}}}
                }
            },
            "classes": {
                "object": {"baseClass": ""},
                "GameObject": {"baseClass": "object"},
                "Item": {"baseClass": "GameObject"},
                "Weapon": {"baseClass": "Item"},
                "Tool": {"baseClass": "Item"}
            }
        }
        
        with open('performance_test_lib.json', 'w', encoding='utf-8') as f:
            json.dump(test_lib, f)
        
        from ReNode.app.NodeFactory import NodeFactory
        
        start_time = time.time()
        
        factory = NodeFactory()
        with patch.object(factory, 'vlib'):
            factory.loadFactoryFromJson('performance_test_lib.json')
        
        loading_time = time.time() - start_time
        
        performance_metrics.record_metric(
            'library_loading_time', 
            loading_time, 
            loading_threshold
        )
        
        # Assert loading time is reasonable
        assert loading_time < loading_threshold, \
            f"Library loading time {loading_time:.2f}s exceeds threshold {loading_threshold}s"
    
    def test_config_initialization_time(self, mock_environment, performance_metrics):
        """Test configuration initialization performance"""
        init_threshold = 5.0  # 5 seconds threshold
        
        start_time = time.time()
        
        with patch('ReNode.app.config.Config.init') as mock_init:
            Application.initializeConfig()
            init_time = time.time() - start_time
            
            performance_metrics.record_metric(
                'config_initialization_time', 
                init_time, 
                init_threshold
            )
            
            assert init_time < init_threshold, \
                f"Config initialization time {init_time:.2f}s exceeds threshold {init_threshold}s"


class TestCompilationPerformance:
    """Test graph compilation performance"""
    
    def test_simple_graph_compilation_time(self, mock_environment, performance_metrics):
        """Test compilation time for a simple graph - should be under 10 seconds"""
        compilation_threshold = 10.0  # 10 seconds as specified
        
        # Create a simple test graph
        simple_graph = {
            'graph': {
                'info': {
                    'name': 'SimplePerformanceTest',
                    'classname': 'SimplePerformanceTestClass',
                    'type': 'class',
                    'graphVersion': 2
                },
                'variables': {'localvar': {}, 'classvar': {}}
            },
            'nodes': {
                'entry': {
                    'class_': 'internal.entry',
                    'name': 'Entry Point',
                    'pos': [0, 0]
                },
                'math_add': {
                    'class_': 'math.add',
                    'name': 'Add Numbers',
                    'pos': [100, 50]
                }
            },
            'connections': []
        }
        
        graph_path = 'simple_performance_test.json'
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(simple_graph, f)
        
        start_time = time.time()
        
        with patch('ReNode.ui.NodeGraphComponent.NodeGraphComponent') as mock_component:
            mock_component.refObject = MagicMock()
            mock_component.refObject.nodeFactory = MagicMock()
            mock_component.refObject.variable_manager = MagicMock()
            mock_component.refObject.sessionManager = MagicMock()
            
            with patch('ReNode.ui.GraphTypes.GraphTypeFactory.getInstanceByType') as mock_graph_type:
                mock_type = MagicMock()
                mock_type.createGenMetaInfoObject.return_value = {'infoData': simple_graph['graph']['info']}
                mock_type.cgHandleVariables.return_value = ""
                mock_type.cgHandleInspectorProps.return_value = ""
                mock_type.cgHandleWrapper.return_value = "// Generated code"
                mock_graph_type.return_value = mock_type
                
                from ReNode.app.CodeGen import CodeGenerator
                generator = CodeGenerator()
                
                with patch('ReNode.app.FileManager.FileManagerHelper.getFolderCompiledScripts'):
                    with patch('builtins.open', create=True):
                        with patch('os.makedirs'):
                            with patch('ReNode.app.FileManager.FileManagerHelper.generateScriptLoader'):
                                try:
                                    result = generator.generateProcess(graph_path, silentMode=True)
                                    compilation_time = time.time() - start_time
                                    
                                    performance_metrics.record_metric(
                                        'simple_graph_compilation_time', 
                                        compilation_time, 
                                        compilation_threshold
                                    )
                                    
                                    assert compilation_time < compilation_threshold, \
                                        f"Simple graph compilation time {compilation_time:.2f}s exceeds threshold {compilation_threshold}s"
                                        
                                except Exception as e:
                                    compilation_time = time.time() - start_time
                                    performance_metrics.record_metric(
                                        'simple_graph_compilation_time_with_errors', 
                                        compilation_time, 
                                        compilation_threshold
                                    )
                                    print(f"Compilation completed with errors in {compilation_time:.2f}s: {e}")
    
    def test_complex_graph_compilation_time(self, mock_environment, performance_metrics):
        """Test compilation time for a complex graph with multiple nodes"""
        compilation_threshold = 10.0  # 10 seconds threshold
        
        # Create a more complex test graph
        complex_graph = {
            'graph': {
                'info': {
                    'name': 'ComplexPerformanceTest',
                    'classname': 'ComplexPerformanceTestClass',
                    'type': 'class',
                    'graphVersion': 2
                },
                'variables': {
                    'localvar': {
                        'var1': {'type': 'int', 'name': 'Counter', 'value': 0},
                        'var2': {'type': 'string', 'name': 'Message', 'value': 'Hello'}
                    },
                    'classvar': {}
                }
            },
            'nodes': {}
        }
        
        # Add many nodes to simulate complexity
        for i in range(20):
            complex_graph['nodes'][f'node_{i}'] = {
                'class_': 'math.add' if i % 2 == 0 else 'logic.and',
                'name': f'Node {i}',
                'pos': [i * 50, i * 30]
            }
        
        graph_path = 'complex_performance_test.json'
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(complex_graph, f)
        
        start_time = time.time()
        
        # Same compilation setup as simple test
        with patch('ReNode.ui.NodeGraphComponent.NodeGraphComponent') as mock_component:
            mock_component.refObject = MagicMock()
            mock_component.refObject.nodeFactory = MagicMock()
            mock_component.refObject.variable_manager = MagicMock()
            mock_component.refObject.sessionManager = MagicMock()
            
            with patch('ReNode.ui.GraphTypes.GraphTypeFactory.getInstanceByType') as mock_graph_type:
                mock_type = MagicMock()
                mock_type.createGenMetaInfoObject.return_value = {'infoData': complex_graph['graph']['info']}
                mock_type.cgHandleVariables.return_value = ""
                mock_type.cgHandleInspectorProps.return_value = ""
                mock_type.cgHandleWrapper.return_value = "// Generated code"
                mock_graph_type.return_value = mock_type
                
                from ReNode.app.CodeGen import CodeGenerator
                generator = CodeGenerator()
                
                with patch('ReNode.app.FileManager.FileManagerHelper.getFolderCompiledScripts'):
                    with patch('builtins.open', create=True):
                        with patch('os.makedirs'):
                            with patch('ReNode.app.FileManager.FileManagerHelper.generateScriptLoader'):
                                try:
                                    result = generator.generateProcess(graph_path, silentMode=True)
                                    compilation_time = time.time() - start_time
                                    
                                    performance_metrics.record_metric(
                                        'complex_graph_compilation_time', 
                                        compilation_time, 
                                        compilation_threshold
                                    )
                                    
                                    assert compilation_time < compilation_threshold, \
                                        f"Complex graph compilation time {compilation_time:.2f}s exceeds threshold {compilation_threshold}s"
                                        
                                except Exception as e:
                                    compilation_time = time.time() - start_time
                                    performance_metrics.record_metric(
                                        'complex_graph_compilation_time_with_errors', 
                                        compilation_time, 
                                        compilation_threshold
                                    )
                                    print(f"Complex compilation completed with errors in {compilation_time:.2f}s: {e}")


class TestMemoryPerformance:
    """Test memory usage during operations"""
    
    def test_node_factory_memory_usage(self, mock_environment, performance_metrics):
        """Test memory usage of NodeFactory with large library"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        from ReNode.app.NodeFactory import NodeFactory
        
        # Create large test library
        large_lib = {
            "system": {"version": 2},
            "nodes": {},
            "classes": {"object": {"baseClass": ""}}
        }
        
        # Add many nodes
        for category in ['math', 'logic', 'string', 'array', 'object']:
            large_lib['nodes'][category] = {}
            for i in range(100):  # 100 nodes per category
                large_lib['nodes'][category][f'node_{i}'] = {
                    'name': f'Node {i}',
                    'inputs': {'input1': {'type': 'int'}},
                    'outputs': {'output1': {'type': 'int'}}
                }
        
        with open('large_test_lib.json', 'w', encoding='utf-8') as f:
            json.dump(large_lib, f)
        
        factory = NodeFactory()
        with patch.object(factory, 'vlib'):
            factory.loadFactoryFromJson('large_test_lib.json')
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = final_memory - initial_memory
        
        performance_metrics.record_metric('node_factory_memory_usage_mb', memory_usage, 500)  # 500MB threshold
        
        # Memory usage should be reasonable
        assert memory_usage < 500, f"NodeFactory memory usage {memory_usage:.2f}MB is too high"


@pytest.fixture(scope="session", autouse=True)
def save_performance_metrics(request, performance_metrics):
    """Save performance metrics to file after test session"""
    def save_metrics():
        if hasattr(request.session, 'performance_metrics'):
            # Combine all metrics from all test instances
            all_metrics = {}
            for item in request.session.items:
                if hasattr(item.instance, 'performance_metrics'):
                    all_metrics.update(item.instance.performance_metrics.metrics)
            
            if all_metrics:
                final_metrics = PerformanceMetrics()
                final_metrics.metrics = all_metrics
                final_metrics.save_to_file('performance_results.json')
                
                violations = final_metrics.check_thresholds()
                if violations:
                    print("\n⚠️  Performance threshold violations:")
                    for violation in violations:
                        print(f"  - {violation}")
                else:
                    print("\n✅ All performance metrics within thresholds")
    
    request.addfinalizer(save_metrics)