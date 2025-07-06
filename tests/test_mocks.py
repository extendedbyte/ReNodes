"""
Mock classes for testing ReNodes without heavy dependencies
"""

class MockQApplication:
    def __init__(self, args=None):
        pass
    
    def exec_(self):
        return 0
    
    def quit(self):
        pass

class MockQWidget:
    def __init__(self):
        pass
    
    def show(self):
        pass
    
    def close(self):
        pass

class MockQMainWindow(MockQWidget):
    def __init__(self):
        super().__init__()

class MockLogger:
    def __init__(self, name):
        self.name = name
    
    def info(self, msg):
        print(f"INFO [{self.name}]: {msg}")
    
    def debug(self, msg):
        print(f"DEBUG [{self.name}]: {msg}")
    
    def error(self, msg):
        print(f"ERROR [{self.name}]: {msg}")
    
    def warning(self, msg):
        print(f"WARNING [{self.name}]: {msg}")

class MockNodeFactory:
    def __init__(self):
        self.nodes = {}
        self.classes = {}
        self.version = 1
        self.graphVersion = 2
    
    def loadFactoryFromJson(self, path, useLoading=False):
        # Mock load - create some basic nodes
        self.nodes = {
            "test.entry": {
                "name": "Entry Point",
                "inputs": {},
                "outputs": {"exec": {"type": "exec"}},
                "code": "// Entry point"
            }
        }
        self.classes = {
            "object": {
                "baseClass": "",
                "fields": {"defined": {}},
                "methods": {"defined": {}}
            }
        }
    
    def getColorByType(self, type_name, retAsQColor=False):
        return [255, 255, 255, 255]
    
    def decomposeType(self, fulltypename):
        return ['value', fulltypename]

class MockCodeGenerator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def compile_graph(self, graph_data):
        return True, "Mock compilation successful"
    
    def generate_code(self, nodes):
        return "// Mock generated code"

class MockApplication:
    @staticmethod
    def isDebugMode():
        return True
    
    @staticmethod
    def hasArgument(arg):
        return False

# Register mock logger function
def MockRegisterLogger(name):
    return MockLogger(name)