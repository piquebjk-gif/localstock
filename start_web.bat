@echo off
chcp 65001 >nul
title MedAjan — Web Panel

set PLAYWRIGHT_BROWSERS_PATH=F:\medajan\playwright_browsers
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
) else if exist "F:\medajan\venv\Scripts\python.exe" (
    set PYTHON=F:\medajan\venv\Scripts\python.exe
) else (
    set PYTHON=python
)

echo Web panel baslatiliyor: http://localhost:8000
echo.
"%PYTHON%" medajan-v21-00.py --nogui

pause
