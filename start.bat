@echo off
title Downloads Monitor - Launcher
color 0A

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

:: Check and activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [WARN] Virtual environment not found, using system Python
)

:: Main Menu
:MENU
cls
echo.
echo ===============================================================
echo                  Downloads Monitor Launcher
echo ===============================================================
echo.
echo Please select an option:
echo.
echo 1. [GUI] Start GUI Application (Recommended)
echo 2. [CLI] Start CLI Application (Command Line)
echo 3. [DBG] GUI with Debug Output
echo 4. [CON] CLI with Continuous Monitoring
echo 5. [EXT] CLI with Extensions Only
echo 6. [INF] Show System Information
echo 7. [DEP] Install/Update Dependencies
echo 8. [CLN] Clean Cache Files
echo 9. [EXT] Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto GUI
if "%choice%"=="2" goto CLI
if "%choice%"=="3" goto GUI_DEBUG
if "%choice%"=="4" goto CLI_CONTINUOUS
if "%choice%"=="5" goto CLI_EXTENSIONS
if "%choice%"=="6" goto SYSTEM_INFO
if "%choice%"=="7" goto INSTALL_DEPS
if "%choice%"=="8" goto CLEANUP
if "%choice%"=="9" goto EXIT

echo Invalid choice. Please try again.
pause
goto MENU

:GUI
echo.
echo [GUI] Starting GUI Application...
echo ===================================
echo.
python gui_app.py
if errorlevel 1 (
    echo.
    echo [ERROR] GUI application failed to start
    echo Please check the error messages above
    pause
)
goto MENU

:CLI
echo.
echo [CLI] Starting CLI Application...
echo ==================================
echo.
python app.py
if errorlevel 1 (
    echo.
    echo [ERROR] CLI application failed to start
    echo Please check the error messages above
    pause
)
goto MENU

:GUI_DEBUG
echo.
echo [DBG] Starting GUI with Debug Output...
echo =====================================
echo.
echo Debug mode will show detailed console output
echo Press Ctrl+C to stop monitoring if needed
echo.
pause
python gui_app.py --log-level DEBUG
if errorlevel 1 (
    echo.
    echo [ERROR] GUI debug mode failed to start
    pause
)
goto MENU

:CLI_CONTINUOUS
echo.
echo [CON] Starting CLI with Continuous Monitoring...
echo ===============================================
echo.
set /p interval="Enter monitoring interval in seconds (default 60): "
if "%interval%"=="" set interval=60
echo Starting continuous monitoring with %interval% second interval...
echo Press Ctrl+C to stop monitoring
echo.
pause
python app.py --continuous %interval%
if errorlevel 1 (
    echo.
    echo [ERROR] Continuous monitoring failed to start
    pause
)
goto MENU

:CLI_EXTENSIONS
echo.
echo [EXT] Running Extensions Only...
echo ================================
echo.
echo This will run analysis on existing data without scanning
echo.
python app.py --ext-only
if errorlevel 1 (
    echo.
    echo [ERROR] Extensions failed to run
    echo Make sure you have run a scan first
    pause
)
pause
goto MENU

:SYSTEM_INFO
echo.
echo [INF] System Information
echo ======================
echo.
python app.py --info
echo.
pause
goto MENU

:INSTALL_DEPS
echo.
echo [DEP] Installing/Updating Dependencies...
echo ========================================
echo.
echo Checking for uv package manager...
uv --version >nul 2>&1
if errorlevel 1 (
    echo uv not found, using pip instead...
    pip install -r requirements.txt
) else (
    echo Using uv for faster dependency management...
    uv sync
)
echo.
echo [OK] Dependencies installation completed
pause
goto MENU

:CLEANUP
echo.
echo [CLN] Cleaning Cache Files...
echo ===========================
echo.
echo Removing Python cache files and compiled bytecode...
python cleanup_cache.py
echo.
echo [OK] Cleanup completed
pause
goto MENU

:EXIT
echo.
echo [BYE] Thank you for using Downloads Monitor!
echo.
timeout /t 2 >nul
exit /b 0
