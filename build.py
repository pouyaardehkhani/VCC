"""
Build script to create standalone EXE using PyInstaller.
Run: python build.py
"""

import subprocess
import sys
import os


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    run_py = os.path.join(script_dir, "run.py")
    icon_path = os.path.join(script_dir, "icon.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "VideoCodecConverter",
        "--icon", icon_path,
        "--add-data", f"vcc;vcc",
        "--add-data", f"icon.ico;.",
        "--noconfirm",
        "--clean",
        run_py,
    ]

    print("Building EXE with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=script_dir)

    if result.returncode == 0:
        exe_path = os.path.join(script_dir, "dist", "VideoCodecConverter.exe")
        print()
        print(f"Build successful!")
        print(f"EXE location: {exe_path}")
    else:
        print(f"Build failed with exit code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
