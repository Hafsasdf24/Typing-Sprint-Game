"""
create_desktop_shortcut.py
Creates a direct Desktop shortcut (.lnk) for Typing Sprint on Windows.
Double-clicking this file will immediately place "Typing Sprint" on your Desktop.
"""

import os
import sys
import subprocess

def get_desktop_path():
    """Find the user's active Windows Desktop path."""
    paths_to_check = []
    
    # 1. Check OneDrive Desktop
    onedrive = os.environ.get("OneDrive")
    if onedrive:
        paths_to_check.append(os.path.join(onedrive, "Desktop"))
        
    # 2. Check standard user profile Desktop
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        paths_to_check.append(os.path.join(userprofile, "Desktop"))
        paths_to_check.append(os.path.join(userprofile, "OneDrive", "Desktop"))
        
    # Return the first one that exists
    for path in paths_to_check:
        if os.path.exists(path):
            return path
            
    return os.path.join(os.path.expanduser("~"), "Desktop")


def create_shortcut():
    desktop = get_desktop_path()
    project_dir = os.path.abspath(os.path.dirname(__file__))
    target_script = os.path.join(project_dir, "typing_sprint_gui.py")
    shortcut_path = os.path.join(desktop, "Typing Sprint.lnk")
    bat_backup_path = os.path.join(desktop, "Typing Sprint.bat")

    # Locate pythonw.exe (runs GUI without a black console window popup)
    python_dir = os.path.dirname(sys.executable)
    pythonw_exe = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = sys.executable

    print(f"Creating Desktop shortcut for Typing Sprint...")
    print(f"Desktop Path: {desktop}")
    print(f"Project Path: {project_dir}")

    # Check for custom icon
    icon_path = os.path.join(project_dir, "assets", "favicon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(project_dir, "assets", "logo.jpg")

    icon_prop = f"$Shortcut.IconLocation = '{icon_path}'" if os.path.exists(icon_path) else ""

    # Method 1: Create Windows .lnk Shortcut using PowerShell WScript.Shell
    ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{pythonw_exe}'
$Shortcut.Arguments = '"{target_script}"'
$Shortcut.WorkingDirectory = '{project_dir}'
$Shortcut.Description = 'Typing Sprint - Falling Words Game'
{icon_prop}
$Shortcut.Save()
"""
    success = False
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True, capture_output=True)
        if os.path.exists(shortcut_path):
            print(f"\n[OK] Windows Shortcut created: {shortcut_path}")
            success = True
    except Exception as e:
        print(f"PowerShell shortcut creation notice: {e}")

    # Method 2: Always create a direct .bat launcher on the desktop as well
    try:
        bat_content = f"""@echo off
cd /d "{project_dir}"
start "" "{pythonw_exe}" "typing_sprint_gui.py"
"""
        with open(bat_backup_path, "w") as f:
            f.write(bat_content)
        print(f"[OK] Desktop Launcher created: {bat_backup_path}")
        success = True
    except Exception as e:
        print(f"Batch creation notice: {e}")

    if success:
        print("\n" + "=" * 55)
        print(" SUCCESS! Typing Sprint is now permanently on your Desktop!")
        print(" You can double-click it anytime directly from your Desktop.")
        print("=" * 55 + "\n")
    else:
        print("\nCould not automatically write to Desktop. Please check permissions.")


if __name__ == "__main__":
    create_shortcut()
