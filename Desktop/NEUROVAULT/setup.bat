@echo off
REM NeuroVault Voice Intelligence System - Setup Script
REM Creates virtual environment and installs dependencies

echo.
echo 🧠 NeuroVault Voice Intelligence System - Setup
echo.
echo This will create a virtual environment and install all dependencies.
echo This may take 5-10 minutes on first run.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3.11+ is not installed or not in PATH.
    echo Please install Python from https://www.python.org
    echo.
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv whisper_env

echo.
echo Activating virtual environment...
call whisper_env\Scripts\activate.bat

echo.
echo Installing dependencies (this will take a few minutes)...
pip install -r requirements.txt

echo.
if errorlevel 1 (
    echo ❌ Setup failed. Check the errors above.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ Setup complete!
    echo.
    echo You can now run the application with:
    echo   run.bat
    echo.
    echo Or manually with:
    echo   whisper_env\Scripts\activate.bat
    echo   python neurovault_app.py
    echo.
    pause
)
