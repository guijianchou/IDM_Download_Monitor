@echo off
title Downloads Monitor

echo Starting Downloads Monitor...
echo.

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Run the program
python app.py

echo.
echo Program completed, press any key to exit...
pause >nul
