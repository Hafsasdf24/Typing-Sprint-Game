@echo off
cd /d "%~dp0"
title Building Typing Sprint Standalone EXE...
echo ============================================================
echo   Building Standalone Typing Sprint.exe with Official Logo
echo ============================================================
python build_exe.py
echo.
pause
