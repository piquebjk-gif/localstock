@echo off
chcp 65001 >nul
title MedAjan v21.00 — Med Tuning Diyarbakır

echo.
echo  ███╗   ███╗███████╗██████╗  █████╗      ██╗ █████╗ ███╗   ██╗
echo  ████╗ ████║██╔════╝██╔══██╗██╔══██╗     ██║██╔══██╗████╗  ██║
echo  ██╔████╔██║█████╗  ██║  ██║███████║     ██║███████║██╔██╗ ██║
echo  ██║╚██╔╝██║██╔══╝  ██║  ██║██╔══██║██   ██║██╔══██║██║╚██╗██║
echo  ██║ ╚═╝ ██║███████╗██████╔╝██║  ██║╚█████╔╝██║  ██║██║ ╚████║
echo  ╚═╝     ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝ ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
echo.
echo  v21.00  ^|  Med Tuning  ^|  Diyarbakır
echo  ─────────────────────────────────────────────────────────────
echo.

:: Playwright tarayıcı dizini
set PLAYWRIGHT_BROWSERS_PATH=F:\medajan\playwright_browsers

:: Proje dizini
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: Python sanal ortamını kontrol et
if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
    echo  [OK] Sanal ortam bulundu: venv\
) else if exist "F:\medajan\venv\Scripts\python.exe" (
    set PYTHON=F:\medajan\venv\Scripts\python.exe
    echo  [OK] Sanal ortam bulundu: F:\medajan\venv\
) else (
    set PYTHON=python
    echo  [!!] Sanal ortam bulunamadi, sistem Python kullaniliyor
)

echo  [**] Playwright dizini: %PLAYWRIGHT_BROWSERS_PATH%
echo  [**] Proje dizini: %PROJECT_DIR%
echo.
echo  Baslatiliyor...
echo.

:: Programı başlat
"%PYTHON%" medajan-v21-00.py

if %errorlevel% neq 0 (
    echo.
    echo  [HATA] Program bir hata ile kapandi. Hata kodu: %errorlevel%
    echo  Loglari kontrol edin: logs\medajan.log
    echo.
    pause
)
