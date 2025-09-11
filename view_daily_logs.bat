@echo off
title Downloads Monitor - Daily Task Logs
color 0B

:: Set working directory to script location
cd /d "%~dp0"

:MENU
cls
echo.
echo ===============================================================
echo                Downloads Monitor - Daily Task Logs
echo ===============================================================
echo.

:: Check if logs directory exists
if not exist "logs" (
    echo [INFO] No logs directory found
    echo Daily tasks haven't been run yet, or logs were deleted
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
)

:: Count log files
set LOG_COUNT=0
for %%f in (logs\daily_*.log) do set /a LOG_COUNT+=1

if %LOG_COUNT% equ 0 (
    echo [INFO] No daily task logs found
    echo Daily tasks haven't been run yet
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
)

echo Found %LOG_COUNT% daily task log(s)
echo.
echo Select an option:
echo.
echo 1. View latest log
echo 2. View all logs (list)
echo 3. Open logs folder
echo 4. Clear old logs (keep last 7 days)
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto VIEW_LATEST
if "%choice%"=="2" goto VIEW_ALL
if "%choice%"=="3" goto OPEN_FOLDER
if "%choice%"=="4" goto CLEAR_LOGS
if "%choice%"=="5" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MENU

:VIEW_LATEST
cls
echo.
echo ========== Latest Daily Task Log ==========
echo.

:: Find the newest log file
for /f "delims=" %%f in ('dir /b /od logs\daily_*.log 2^>nul') do set LATEST=%%f

if defined LATEST (
    echo Log file: logs\%LATEST%
    echo.
    type "logs\%LATEST%"
) else (
    echo No log files found.
)

echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:VIEW_ALL
cls
echo.
echo ========== All Daily Task Logs ==========
echo.

echo Available log files:
echo.
dir /b /od logs\daily_*.log 2>nul

echo.
set /p logfile="Enter log filename (or press Enter to return): "

if "%logfile%"=="" goto MENU

if exist "logs\%logfile%" (
    cls
    echo.
    echo ========== Log: %logfile% ==========
    echo.
    type "logs\%logfile%"
    echo.
    echo Press any key to return to menu...
    pause >nul
) else (
    echo.
    echo [ERROR] Log file not found: %logfile%
    timeout /t 2 >nul
)
goto MENU

:OPEN_FOLDER
start "" explorer "%~dp0logs"
goto MENU

:CLEAR_LOGS
cls
echo.
echo ========== Clear Old Logs ==========
echo.
echo This will delete logs older than 7 days.
echo.
set /p confirm="Are you sure? (Y/N): "

if /i "%confirm%"=="Y" (
    echo.
    echo Clearing old logs...
    
    :: Delete files older than 7 days
    forfiles /p logs /s /m daily_*.log /d -7 /c "cmd /c echo Deleting @file && del @path" 2>nul
    
    echo.
    echo Old logs cleared.
    timeout /t 2 >nul
) else (
    echo.
    echo Operation cancelled.
    timeout /t 1 >nul
)
goto MENU

:EXIT
echo.
echo Thank you for using Downloads Monitor!
timeout /t 1 >nul
exit /b 0
