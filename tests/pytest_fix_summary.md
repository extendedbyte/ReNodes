# PyQt5 Import Issues Fixed for pytest

## Issues Resolved

### 1. PyQt5 Module Import Errors
**Problem**: `cannot import name 'QMessageBox' from 'PyQt5.QtWidgets'`

**Solution**: Created comprehensive PyQt5/Qt stub system:
- `tests/pyqt5_stub_helper.py` - Complete stub implementation
- Updated `tests/conftest.py` to import stubs before any PyQt5 imports
- Added all required PyQt5 classes and Qt constants

### 2. pytest Collection Errors
**Problem**: pytest was trying to collect `run_app_test.py` which calls `sys.exit(1)`

**Solution**: 
- Renamed `run_app_test.py` to `standalone_app_test.py`
- Added `--ignore` rules in `pytest.ini`
- Created separate test files for pytest vs standalone testing

### 3. Missing PyQt5 Classes and Constants
**Problem**: Various missing classes like `QUndoCommand`, `QGraphicsItem`, Qt constants

**Solution**: Extended stub helper with:
- All QtWidgets classes (QMessageBox, QUndoCommand, QGraphicsItem, etc.)
- All QtGui classes (QColor, QPixmap, QIcon, etc.) 
- All QtCore classes (QObject, QTimer, QSettings, etc.)
- Qt namespace constants (SolidLine, mouse buttons, focus policies, etc.)
- Specialized handling for QGraphicsItem with all its flags/constants

### 4. Missing distutils Module (Python 3.12+)
**Problem**: `No module named 'distutils'` 

**Solution**: Added distutils.version.LooseVersion stub in pyqt5_stub_helper.py

### 5. SIP Module Missing
**Problem**: `from PyQt5.sip import isdeleted` failed

**Solution**: Created sip module stub with isdeleted and delete functions

## Files Created/Modified

### New Files:
- `tests/pyqt5_stub_helper.py` - Comprehensive PyQt5/Qt stub system
- `tests/standalone_app_test.py` - Standalone app test (not for pytest)
- `tests/test_imports.py` - Pytest-compatible import tests

### Modified Files:
- `tests/conftest.py` - Updated to use comprehensive stubs
- `pytest.ini` - Added ignore rules for non-pytest files
- `.github/workflows/test.yml` - Added standalone test step
- `ReNode/app/CodeGen.py` - Fixed regex escape sequences
- `ReNode/app/utils.py` - Fixed regex escape sequence

### Deleted Files:
- `tests/run_app_test.py` - Replaced with standalone_app_test.py

## PyQt5 Classes Supported

### QtWidgets:
QApplication, QWidget, QMainWindow, QDialog, QMessageBox, QMenu, QMenuBar, QAction, QToolBar, QStatusBar, QPushButton, QLabel, QLineEdit, QTextEdit, QTextBrowser, QComboBox, QCheckBox, QRadioButton, QSpinBox, QSlider, QListWidget, QTreeWidget, QTreeWidgetItem, QTableWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QDockWidget, QTabWidget, QStackedWidget, QScrollArea, QSplashScreen, QProgressBar, QFileDialog, QInputDialog, QCompleter, QListView, QGroupBox, QFrame, QSplitter, QGraphicsItem, QGraphicsScene, QGraphicsView, QGraphicsWidget, QGraphicsProxyWidget, QGraphicsTextItem, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPathItem, QGraphicsPolygonItem, QGraphicsSimpleTextItem, QUndoCommand, QUndoStack, QOpenGLWidget, QStyleOptionGraphicsItem

### QtGui:
QColor, QPixmap, QIcon, QPainter, QFont, QBrush, QPen, QTextDocument, QTextCursor, QTextFormat, QTextCharFormat, QPalette, QImage, QCursor, QKeySequence

### QtCore:
pyqtSignal, Signal, QThread, QTimer, QSettings, QObject, Qt (namespace)

## Qt Constants Supported

Window hints, mouse buttons, key codes, alignment flags, pen styles, brush styles, cursor shapes, focus policies, graphics item flags, text flags, dock widget areas, and more.

## Test Strategy

1. **PyQt5 Stubs**: Comprehensive mocking for CI environments without GUI libraries
2. **Fallback System**: conftest.py tries comprehensive stubs first, falls back to basic stubs
3. **Separation**: pytest tests vs standalone tests kept separate
4. **Graceful Degradation**: Tests skip/warn when dependencies missing rather than failing

## Result

pytest now runs without PyQt5 import errors, and comprehensive testing is possible in CI environments without GUI dependencies.