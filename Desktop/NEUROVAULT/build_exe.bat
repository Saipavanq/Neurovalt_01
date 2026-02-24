@echo off
REM NeuroVault Standalone Executable Builder
REM Converts neurovault_app.py to standalone neurovault_app.exe

echo 🧠 NeuroVault - Building Standalone Executable...
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Building executable (this may take 2-3 minutes)...
echo.

REM Build command with all hidden imports
pyinstaller --onefile ^
    --windowed ^
    --name "NeuroVault" ^
    --icon=icon.ico ^
    --hidden-import=tkinter ^
    --hidden-import=sounddevice ^
    --hidden-import=scipy ^
    --hidden-import=numpy ^
    --hidden-import=faster_whisper ^
    --hidden-import=transformers ^
    --hidden-import=sentence_transformers ^
    --hidden-import=faiss ^
    --hidden-import=torch ^
    --hidden-import=pyannote.audio ^
    --add-data "memory_history.json:." ^
    --add-data "faiss_index.bin:." ^
    --distpath dist ^
    neurovault_app.py

echo.
if exist dist\NeuroVault.exe (
    echo.
    echo ✅ Success! Executable created at: dist\NeuroVault.exe
    echo.
    echo You can now distribute this .exe file without requiring Python installation.
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed. Check console output above for errors.
    echo.
    pause
)
