"""
Build script for creating a standalone executable
"""

import subprocess
import sys
import os

def build():
    """Build the executable using PyInstaller"""
    
    print("=" * 60)
    print("Bin Day Brain - Building Executable")
    print("=" * 60)
    print()
    
    # Check if icon exists
    icon_arg = ""
    data_arg = ""

    # Check for ICO icon (for Windows executable icon)
    if os.path.exists("app_icon.ico"):
        icon_arg = "--icon=app_icon.ico"
        print("[OK] Found app icon (ICO)")
    elif os.path.exists("bin-day-brain-icon.png"):
        print("! Found PNG icon but no ICO icon - executable will use default Windows icon")
    else:
        print("! No app icon found - building without icon")

    # Check for PNG icon (for window taskbar icon)
    if os.path.exists("bin-day-brain-icon.png"):
        data_arg = "--add-data=bin-day-brain-icon.png;."
        print("[OK] Found window icon (PNG) - will be included")

    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=bin-day-brain",
    ]

    if icon_arg:
        cmd.append(icon_arg)

    if data_arg:
        cmd.append(data_arg)

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
        print("[OK] Build successful!")
        print("=" * 60)
        print()
        print("The executable can be found at:")
        print("  dist/bin-day-brain.exe")
        print()
        print("You can distribute this single file - no installation needed!")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("[FAIL] Build failed!")
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
        print("[FAIL] PyInstaller not found!")
        print("=" * 60)
        print()
        print("Please install PyInstaller:")
        print("  pip install pyinstaller")
        print()
        sys.exit(1)


if __name__ == "__main__":
    build()
