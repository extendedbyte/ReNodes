#!/usr/bin/env python3
"""Comprehensive PyQt5/Qt stub helper for testing without GUI dependencies"""

import sys
import types
import importlib

def create_pyqt5_stubs():
    """Create comprehensive PyQt5/Qt stubs for testing"""
    
    # Create mock pyqtSignal class
    class MockSignal:
        def __init__(self, *args, **kwargs):
            pass
        def emit(self, *args, **kwargs):
            pass
        def connect(self, func):
            pass
        def disconnect(self, func=None):
            pass
    
    # Create mock QThread
    class MockQThread:
        def __init__(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def quit(self):
            pass
        def wait(self):
            pass
        def isRunning(self):
            return False
        
    # Create sip module stub
    sip_stub = types.ModuleType("sip")
    sip_stub.isdeleted = lambda obj: False
    sip_stub.delete = lambda obj: None
    sys.modules["PyQt5.sip"] = sip_stub
    sys.modules["sip"] = sip_stub
    
    # Create distutils stub for Python 3.12+
    class LooseVersion:
        def __init__(self, version):
            self.version = str(version)
        def __lt__(self, other):
            return False
        def __le__(self, other):
            return True
        def __gt__(self, other):
            return False
        def __ge__(self, other):
            return True
        def __eq__(self, other):
            return True
        def __str__(self):
            return self.version
    
    distutils_stub = types.ModuleType("distutils")
    distutils_version_stub = types.ModuleType("distutils.version")
    distutils_version_stub.LooseVersion = LooseVersion
    sys.modules["distutils"] = distutils_stub
    sys.modules["distutils.version"] = distutils_version_stub
    distutils_stub.version = distutils_version_stub
    
    for mod_name in ("PyQt5", "Qt"):
        try:
            importlib.import_module(mod_name)
        except (ModuleNotFoundError, ImportError):
            qt_stub = types.ModuleType(mod_name)
            sys.modules[mod_name] = qt_stub
            
            # Create submodules
            for sub in ("QtWidgets", "QtCore", "QtGui"):
                sub_mod_name = f"{mod_name}.{sub}"
                sub_mod = types.ModuleType(sub_mod_name)
                sys.modules[sub_mod_name] = sub_mod
                setattr(qt_stub, sub, sub_mod)
                
                # Add pyqtSignal and Signal to QtCore
                if sub == "QtCore":
                    setattr(sub_mod, "pyqtSignal", MockSignal)
                    setattr(sub_mod, "Signal", MockSignal)
                    setattr(sub_mod, "QThread", MockQThread)
                    setattr(sub_mod, "QTimer", type("QTimer", (), {
                        "__init__": lambda self, *a, **k: None,
                        "start": lambda self, *a: None,
                        "stop": lambda self: None,
                        "timeout": MockSignal(),
                        "setInterval": lambda self, ms: None,
                        "singleShot": staticmethod(lambda ms, func: func()),
                    }))
                    setattr(sub_mod, "QSettings", type("QSettings", (), {
                        "__init__": lambda self, *a, **k: None,
                        "value": lambda self, key, default=None: default,
                        "setValue": lambda self, key, value: None,
                        "sync": lambda self: None,
                        "beginGroup": lambda self, prefix: None,
                        "endGroup": lambda self: None,
                    }))
                    # Add Qt namespace
                    setattr(sub_mod, "Qt", type("Qt", (), {
                        "WindowMinimizeButtonHint": 1,
                        "WindowMaximizeButtonHint": 2,
                        "WindowCloseButtonHint": 4,
                        "WindowStaysOnTopHint": 8,
                        "Key_Escape": 16777216,
                        "LeftButton": 1,
                        "RightButton": 2,
                        "MiddleButton": 4,
                        "AlignLeft": 1,
                        "AlignRight": 2,
                        "AlignCenter": 4,
                        "AlignTop": 8,
                        "AlignBottom": 16,
                        "UserRole": 256,
                        # Pen styles
                        "SolidLine": 1,
                        "DashLine": 2,
                        "DotLine": 3,
                        "DashDotLine": 4,
                        "DashDotDotLine": 5,
                        "NoPen": 0,
                        # Brush styles
                        "SolidPattern": 1,
                        "NoBrush": 0,
                        # Cursor shapes
                        "ArrowCursor": 0,
                        "UpArrowCursor": 1,
                        "CrossCursor": 2,
                        "WaitCursor": 3,
                        "IBeamCursor": 4,
                        "SizeVerCursor": 5,
                        "SizeHorCursor": 6,
                        "SizeBDiagCursor": 7,
                        "SizeFDiagCursor": 8,
                        "SizeAllCursor": 9,
                        "BlankCursor": 10,
                        "SplitVCursor": 11,
                        "SplitHCursor": 12,
                        "PointingHandCursor": 13,
                        "ForbiddenCursor": 14,
                        "WhatsThisCursor": 15,
                        "BusyCursor": 16,
                        # Focus policies
                        "NoFocus": 0,
                        "TabFocus": 1,
                        "ClickFocus": 2,
                        "StrongFocus": 11,
                        "WheelFocus": 15,
                        # Graphics Item flags and types
                        "UserType": 65536,
                        "ItemIsMovable": 1,
                        "ItemIsSelectable": 2,
                        "ItemIsFocusable": 4,
                        # Text flags
                        "TextWordWrap": 1,
                        "TextSingleLine": 256,
                        # Dock widget areas
                        "LeftDockWidgetArea": 1,
                        "RightDockWidgetArea": 2,
                        "TopDockWidgetArea": 4,
                        "BottomDockWidgetArea": 8,
                    }))
                
                # GUI classes for QtGui
                if sub == "QtGui":
                    gui_classes = ["QColor", "QPixmap", "QIcon", "QPainter", "QFont", "QBrush", "QPen", 
                                  "QTextDocument", "QTextCursor", "QTextFormat", "QTextCharFormat",
                                  "QPalette", "QImage", "QCursor", "QKeySequence"]
                    for cls in gui_classes:
                        if cls == "QColor":
                            color_class = type(cls, (), {
                                "__init__": lambda self, *a, **k: None,
                                "red": lambda self: 0,
                                "green": lambda self: 0,
                                "blue": lambda self: 0,
                                "alpha": lambda self: 255,
                                "setRed": lambda self, v: None,
                                "setGreen": lambda self, v: None,
                                "setBlue": lambda self, v: None,
                                "setAlpha": lambda self, v: None,
                                "name": lambda self: "#000000",
                            })
                            setattr(sub_mod, cls, color_class)
                        else:
                            stub_class = type(cls, (), {
                                "__init__": lambda self, *a, **k: None,
                            })
                            setattr(sub_mod, cls, stub_class)
                
                # Widget classes for QtWidgets
                if sub == "QtWidgets":
                    widget_classes = [
                        "QApplication", "QWidget", "QMainWindow", "QDialog", "QMessageBox",
                        "QMenu", "QMenuBar", "QAction", "QToolBar", "QStatusBar",
                        "QPushButton", "QLabel", "QLineEdit", "QTextEdit", "QTextBrowser",
                        "QComboBox", "QCheckBox", "QRadioButton", "QSpinBox", "QSlider",
                        "QListWidget", "QTreeWidget", "QTreeWidgetItem", "QTableWidget",
                        "QVBoxLayout", "QHBoxLayout", "QGridLayout", "QFormLayout",
                        "QDockWidget", "QTabWidget", "QStackedWidget", "QScrollArea",
                        "QSplashScreen", "QProgressBar", "QFileDialog", "QInputDialog",
                        "QCompleter", "QListView", "QGroupBox", "QFrame", "QSplitter",
                        "QGraphicsItem", "QGraphicsScene", "QGraphicsView", "QGraphicsWidget",
                        "QGraphicsProxyWidget", "QGraphicsTextItem", "QGraphicsPixmapItem",
                        "QGraphicsRectItem", "QGraphicsEllipseItem", "QGraphicsLineItem",
                        "QGraphicsPathItem", "QGraphicsPolygonItem", "QGraphicsSimpleTextItem",
                        "QUndoCommand", "QUndoStack", "QOpenGLWidget", "QStyleOptionGraphicsItem"
                    ]
                    
                    for cls in widget_classes:
                        if cls == "QApplication":
                            app_class = type(cls, (), {
                                "__init__": lambda self, *a, **k: None,
                                "instance": classmethod(lambda cls: None),
                                "setQuitOnLastWindowClosed": lambda self, flag: None,
                                "quit": lambda self: None,
                                "exec_": lambda self: 0,
                                "exec": lambda self: 0,
                                "processEvents": classmethod(lambda cls: None),
                                "clipboard": classmethod(lambda cls: type("Clipboard", (), {"setText": lambda s, t: None})()),
                            })
                            setattr(sub_mod, cls, app_class)
                        elif cls == "QFileDialog":
                            fd_class = type(cls, (), {
                                "__init__": lambda self, *a, **k: None,
                                "getOpenFileName": staticmethod(lambda *a, **k: ("", "")),
                                "getSaveFileName": staticmethod(lambda *a, **k: ("", "")),
                                "getExistingDirectory": staticmethod(lambda *a, **k: ""),
                            })
                            setattr(sub_mod, cls, fd_class)
                        elif cls == "QMessageBox":
                            mb_class = type(cls, (), {
                                "__init__": lambda self, *a, **k: None,
                                "information": staticmethod(lambda *a, **k: None),
                                "warning": staticmethod(lambda *a, **k: None),
                                "critical": staticmethod(lambda *a, **k: None),
                                "question": staticmethod(lambda *a, **k: 0),
                                "Yes": 1,
                                "No": 2,
                                "Cancel": 4,
                                "Ok": 8,
                            })
                            setattr(sub_mod, cls, mb_class)
                        elif cls == "QGraphicsItem":
                            gi_class = type(cls, (), {
                                "__init__": lambda self, *a, **k: None,
                                "DeviceCoordinateCache": 1,
                                "NoCache": 0,
                                "ItemCoordinateCache": 2,
                                "ItemIsMovable": 1,
                                "ItemIsSelectable": 2,
                                "ItemIsFocusable": 4,
                                "ItemClipsToShape": 8,
                                "ItemClipsChildrenToShape": 16,
                                "ItemIgnoresTransformations": 32,
                                "ItemIgnoresParentOpacity": 64,
                                "ItemDoesntPropagateOpacityToChildren": 128,
                                "ItemStacksBehindParent": 256,
                                "ItemUsesExtendedStyleOption": 512,
                                "ItemHasNoContents": 1024,
                                "ItemSendsGeometryChanges": 2048,
                                "ItemAcceptsInputMethod": 4096,
                                "ItemNegativeZStacksBehindParent": 8192,
                                "ItemIsPanel": 16384,
                                "ItemSendsScenePositionChanges": 32768,
                                "setPos": lambda self, *a: None,
                                "pos": lambda self: None,
                                "scene": lambda self: None,
                                "show": lambda self: None,
                                "hide": lambda self: None,
                                "setVisible": lambda self, v: None,
                                "update": lambda self: None,
                                "parentItem": lambda self: None,
                                "setParentItem": lambda self, p: None,
                            })
                            setattr(sub_mod, cls, gi_class)
                        else:
                            stub_class = type(cls, (), {
                                "__init__": lambda self, *a, **k: None,
                                "show": lambda self: None,
                                "hide": lambda self: None,
                                "close": lambda self: None,
                                "exec_": lambda self: 0,
                                "exec": lambda self: 0,
                                "setText": lambda self, *a: None,
                                "text": lambda self: "",
                                "setPixmap": lambda self, *a: None,
                                "addWidget": lambda self, *a: None,
                                "setLayout": lambda self, *a: None,
                                "addAction": lambda self, *a: None,
                                "addMenu": lambda self, *a: None,
                                "setMenuBar": lambda self, *a: None,
                                "setEnabled": lambda self, v: None,
                                "setVisible": lambda self, v: None,
                                "setWindowTitle": lambda self, t: None,
                                "setGeometry": lambda self, *a: None,
                                "resize": lambda self, *a: None,
                                "move": lambda self, *a: None,
                                "parent": lambda self: None,
                                "deleteLater": lambda self: None,
                                "update": lambda self: None,
                            })
                            setattr(sub_mod, cls, stub_class)
                
                # Common enums/constants
                setattr(sub_mod, "QT_VERSION_STR", "stub-5.15.0")
    
    # Create main PyQt5 attributes
    if "PyQt5" in sys.modules:
        pyqt5 = sys.modules["PyQt5"]
        # Import all created submodules into main module
        pyqt5.QtWidgets = sys.modules.get("PyQt5.QtWidgets")
        pyqt5.QtCore = sys.modules.get("PyQt5.QtCore")
        pyqt5.QtGui = sys.modules.get("PyQt5.QtGui")
        pyqt5.sip = sip_stub
        
    return True

# Auto-create stubs when imported
create_pyqt5_stubs()