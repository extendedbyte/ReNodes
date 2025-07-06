@echo off
echo ================================================================
echo              ReNodes Quick Test Runner
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo Python found. Starting tests...
echo.

REM Run the test script
python run_tests_local.py

echo.
echo ================================================================
echo Tests completed. Check the output above for results.
echo ================================================================
pause