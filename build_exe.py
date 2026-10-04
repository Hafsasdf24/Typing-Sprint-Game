"""
build_exe.py
Automated script to build a standalone, single-file Windows Executable (Typing Sprint.exe).
"""

import os
import sys
import shutil
import subprocess

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

AI_GEN_LOGO = r"C:\Users\Usman Computers\.gemini\antigravity-ide\brain\4c9c54bf-9f8a-4601-b233-5e40f0b7e223\typing_sprint_logo_1791110616790.jpg"
LOGO_JPG = os.path.join(ASSETS_DIR, "logo.jpg")
ICO_PATH = os.path.join(ASSETS_DIR, "favicon.ico")

print("=" * 60)
print("     ⚡ TYPING SPRINT - STANDALONE EXE BUILDER ⚡")
print("=" * 60)

# 1. Ensure logo image is present in assets
if not os.path.exists(LOGO_JPG) and os.path.exists(AI_GEN_LOGO):
    print("[1/5] Copying official logo to assets...")
    shutil.copyfile(AI_GEN_LOGO, LOGO_JPG)

# 2. Check/Install Pillow and PyInstaller
print("\n[2/5] Checking dependencies (PyInstaller & Pillow)...")
try:
    import PIL
except ImportError:
    print("  Installing Pillow...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    import PIL

try:
    import PyInstaller
except ImportError:
    print("  Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# 3. Generate .ico for Windows Executable
print("\n[3/5] Generating Windows application icon (.ico)...")
if os.path.exists(LOGO_JPG):
    try:
        from PIL import Image
        img = Image.open(LOGO_JPG)
        img.save(ICO_PATH, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print(f"  [OK] Created {ICO_PATH}")
    except Exception as e:
        print(f"  Warning creating .ico: {e}")

# 4. Run PyInstaller
print("\n[4/5] Compiling Typing Sprint into standalone .exe...")
pyinstaller_args = [
    sys.executable, "-m", "PyInstaller",
    "--noconsole",
    "--onefile",
    "--name=Typing Sprint",
    "--clean",
    "typing_sprint_gui.py"
]

if os.path.exists(ICO_PATH):
    pyinstaller_args.insert(-1, f"--icon={ICO_PATH}")

if os.path.exists(ASSETS_DIR):
    # Windows format: source;dest
    pyinstaller_args.insert(-1, f"--add-data={ASSETS_DIR};assets")

print(f"  Running: {' '.join(pyinstaller_args)}")
result = subprocess.run(pyinstaller_args, cwd=PROJECT_DIR)

if result.returncode != 0:
    print("\n[ERROR] PyInstaller compilation failed. See output above.")
    sys.exit(result.returncode)

# 5. Move .exe to project root for easy access
dist_exe = os.path.join(PROJECT_DIR, "dist", "Typing Sprint.exe")
target_exe = os.path.join(PROJECT_DIR, "Typing Sprint.exe")

if os.path.exists(dist_exe):
    print("\n[5/5] Finalizing executable...")
    shutil.copyfile(dist_exe, target_exe)
    print("=" * 60)
    print("  SUCCESS! Standalone Executable Created:")
    print(f"  -> {target_exe}")
    print("=" * 60)
    print("You can run 'Typing Sprint.exe' directly without Python!")
else:
    print(f"\n[!] Built file not found at {dist_exe}")
