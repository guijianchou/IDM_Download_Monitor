@echo off
:: Downloads Monitor - Quick GUI Launcher
:: Launches GUI silently without showing terminal window

setlocal

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    :: Only show error if Python is missing
    title Downloads Monitor - Error
    echo.
    echo [ERROR] Python is not installed or not found in PATH
    echo.
    echo Please install Python 3.8+ and ensure it's added to PATH
    echo Download from: https://python.org
    echo.
    pause
    exit /b 1
)

:: Check if GUI file exists
if not exist "gui_app.py" (
    title Downloads Monitor - Error
    echo.
    echo [ERROR] GUI application file not found
    echo.
    echo Please ensure gui_app.py is in the same folder as this script
    echo.
    pause
    exit /b 1
)

:: Set working directory to script location
cd /d "%~dp0"

:: Check and activate virtual environment if exists (silently)
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat" >nul 2>&1
)

:: Launch GUI application without console window
:: Use pythonw for completely silent execution
pythonw gui_app.py >nul 2>&1
if errorlevel 1 (
    :: If pythonw fails, try with regular python minimized
    start "Downloads Monitor GUI" /min python gui_app.py
)

:: Exit silently
exit /b 0
