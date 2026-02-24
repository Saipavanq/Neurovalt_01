@echo off
REM NeuroVault Voice Intelligence System - Windows Launcher
REM Activates virtual environment and launches the application

echo.
echo 🧠 NeuroVault Voice Intelligence System
echo.

REM Check if virtual environment exists
if not exist whisper_env (
    echo Error: Virtual environment not found!
    echo Please navigate to the NEUROVAULT folder and run setup first.
    echo.
    echo Run: python -m venv whisper_env
    echo Then: whisper_env\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment and run the app
call whisper_env\Scripts\activate.bat
python neurovault_app.py

if errorlevel 1 (
    echo.
    echo Error running the application.
    pause
    exit /b 1
)
