#!/usr/bin/env python3
"""Test PyQt5 stub functionality without pytest"""

import sys
import types
import importlib

# ---------------------------------------------------------------------------
# Stub Qt/PyQt5 modules (for CI environments without GUI libraries)
# ---------------------------------------------------------------------------
for mod_name in ("PyQt5", "Qt"):
    try:
        importlib.import_module(mod_name)
    except ModuleNotFoundError:
        qt_stub = types.ModuleType(mod_name)
        sys.modules[mod_name] = qt_stub
        # Create submodules commonly used
        for sub in ("QtWidgets", "QtCore", "QtGui"):
            sub_mod_name = f"{mod_name}.{sub}"
            sub_mod = types.ModuleType(sub_mod_name)
            sys.modules[sub_mod_name] = sub_mod
            setattr(qt_stub, sub, sub_mod)
            # Provide minimal stub classes/attributes
            for cls in ("QApplication", "QWidget", "QMainWindow", "QObject"):
                stub_class = type(cls, (), {
                    "__init__": lambda self, *a, **k: None,
                    "instance": classmethod(lambda cls: None),
                    "setQuitOnLastWindowClosed": lambda self, flag: None,
                    "quit": lambda self: None
                })
                setattr(sub_mod, cls, stub_class)
            # Basic enums/constants placeholder
            setattr(sub_mod, "QT_VERSION_STR", "stub-0")

# Test imports
try:
    from PyQt5.QtWidgets import QApplication
    print("✅ PyQt5.QtWidgets.QApplication imported successfully")
    
    from PyQt5.QtCore import QObject
    print("✅ PyQt5.QtCore.QObject imported successfully")
    
    from Qt.QtWidgets import QMainWindow  
    print("✅ Qt.QtWidgets.QMainWindow imported successfully")
    
    # Test creating instance
    app = QApplication([])
    print("✅ QApplication instance created successfully")
    
    print("🎉 All PyQt5 stub tests passed!")
    
except Exception as e:
    print(f"❌ PyQt5 stub test failed: {e}")
    sys.exit(1)