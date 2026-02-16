import os
import subprocess
import sys

def build():
    # Install pyinstaller if not present
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Run PyInstaller
    print("Building SafePaste executable...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", "SafePaste.spec", "--clean", "--noconfirm"])
    
    print("Build complete. Check dist/SafePaste/")

if __name__ == "__main__":
    build()
