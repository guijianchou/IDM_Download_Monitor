@echo off
:: Downloads Monitor - Daily Scheduled Task Runner
:: Runs monitoring silently in background for Windows Task Scheduler
:: No windows will be shown during execution

setlocal

:: Set working directory to script location
cd /d "%~dp0"

:: Create log directory if it doesn't exist
if not exist "logs" mkdir logs

:: Set log file with timestamp
for /f "tokens=1-3 delims=/" %%a in ('date /t') do (
    set TODAY=%%c-%%a-%%b
)
for /f "tokens=1-2 delims=:" %%a in ('time /t') do (
    set NOW=%%a-%%b
)
set LOGFILE=logs\daily_%TODAY%_%NOW::=%.log

:: Redirect all output to log file
(
    echo ========================================
    echo Downloads Monitor Daily Task
    echo Started: %date% %time%
    echo ========================================
    echo.

    :: Check if Python is available
    python --version 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not found in PATH
        echo Task failed - Python not available
        goto :ERROR_END
    )

    :: Check if main application exists
    if not exist "app.py" (
        echo [ERROR] Main application file app.py not found
        echo Task failed - Missing application files
        goto :ERROR_END
    )

    :: Activate virtual environment if exists
    if exist ".venv\Scripts\activate.bat" (
        echo [INFO] Activating virtual environment...
        call ".venv\Scripts\activate.bat"
        if errorlevel 1 (
            echo [WARN] Virtual environment activation failed, using system Python
        ) else (
            echo [INFO] Virtual environment activated successfully
        )
    ) else (
        echo [INFO] No virtual environment found, using system Python
    )

    :: Run daily monitoring task
    echo.
    echo [TASK] Starting daily Downloads folder monitoring...
    echo Command: python app.py --log-level INFO
    echo.
    
    python app.py --log-level INFO 2>&1
    set EXIT_CODE=!errorlevel!
    
    echo.
    echo [TASK] Monitoring completed with exit code: !EXIT_CODE!
    
    if !EXIT_CODE! equ 0 (
        echo [SUCCESS] Daily monitoring task completed successfully
    ) else (
        echo [ERROR] Daily monitoring task failed with code !EXIT_CODE!
    )
    
    echo.
    echo ========================================
    echo Task finished: %date% %time%
    echo ========================================
    
    goto :END

    :ERROR_END
    echo.
    echo ========================================  
    echo Task failed: %date% %time%
    echo ========================================

    :END
) > "%LOGFILE%" 2>&1

:: Always exit with code 0 for Task Scheduler (prevents retry loops)
:: Check the log file for actual results
exit /b 0
