#!/usr/bin/env python
"""
NeuroVault Standalone Executable Builder
Converts neurovault_app.py to standalone executable
"""

import subprocess
import sys
import os

def build_executable():
    print("🧠 NeuroVault - Building Standalone Executable...")
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    print()
    print("Building executable (this may take 2-3 minutes)...")
    print()
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "NeuroVault",
        "--hidden-import=tkinter",
        "--hidden-import=sounddevice",
        "--hidden-import=scipy",
        "--hidden-import=numpy",
        "--hidden-import=faster_whisper",
        "--hidden-import=transformers",
        "--hidden-import=sentence_transformers",
        "--hidden-import=faiss",
        "--hidden-import=torch",
        "--hidden-import=pyannote.audio",
        "--distpath", "dist",
        "neurovault_app.py"
    ]
    
    # Add icon if it exists
    if os.path.exists("icon.ico"):
        cmd.extend(["--icon=icon.ico"])
    
    # Run PyInstaller
    result = subprocess.run(cmd)
    
    print()
    if os.path.exists("dist/NeuroVault.exe") or os.path.exists("dist/NeuroVault"):
        print("✅ Success! Executable created at:")
        if sys.platform == "win32":
            print("   dist\\NeuroVault.exe")
        else:
            print("   dist/NeuroVault")
        print()
        print("You can now distribute this executable without requiring Python installation.")
    else:
        print("❌ Build failed. Check console output above for errors.")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(build_executable())
