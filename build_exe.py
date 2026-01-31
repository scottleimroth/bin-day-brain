"""
Build script for creating a standalone executable
"""

import subprocess
import sys
import os

def build():
    """Build the executable using PyInstaller"""
    
    print("=" * 60)
    print("FOGI App - Building Executable")
    print("=" * 60)
    print()
    
    # Check if icon exists
    icon_arg = ""
    if os.path.exists("app_icon.ico"):
        icon_arg = "--icon=app_icon.ico"
        print("✓ Found app icon")
    else:
        print("! No app icon found (app_icon.ico) - building without icon")
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=fogi-app",
    ]
    
    if icon_arg:
        cmd.append(icon_arg)
    
    cmd.append("main.py")
    
    print()
    print("Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True)
        
        print()
        print("=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print()
        print("The executable can be found at:")
        print("  dist/fogi-app.exe")
        print()
        print("You can distribute this single file - no installation needed!")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Make sure you have installed PyInstaller:")
        print("  pip install pyinstaller")
        print()
        sys.exit(1)
    
    except FileNotFoundError:
        print()
        print("=" * 60)
        print("✗ PyInstaller not found!")
        print("=" * 60)
        print()
        print("Please install PyInstaller:")
        print("  pip install pyinstaller")
        print()
        sys.exit(1)


if __name__ == "__main__":
    build()
