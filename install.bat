@echo off
chcp 65001 >nul
title MedAjan v21.00 — Kurulum

echo.
echo  MedAjan v21.00 — Kurulum Basliyor
echo  Med Tuning ^| Diyarbakir
echo  ══════════════════════════════════
echo.

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Python 3.10+ yukleyin: https://python.org
    pause
    exit /b 1
)

echo [1/5] Sanal ortam olusturuluyor...
if not exist "venv" (
    python -m venv venv
    echo       Sanal ortam olusturuldu: venv\
) else (
    echo       Sanal ortam zaten mevcut.
)

echo.
echo [2/5] pip guncelleniyor...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet

echo.
echo [3/5] Gerekli kutuphaneler yukleniyor...
echo       (Bu islem 5-10 dakika surebilir)
echo.
venv\Scripts\pip.exe install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo.
    echo [!!] Bazi paketler yuklenemedi. Tek tek deneniyor...
    for /f "tokens=1 delims==" %%p in (requirements.txt) do (
        venv\Scripts\pip.exe install "%%p" --quiet 2>nul
    )
)

echo.
echo [4/5] Playwright Chromium tarayicisi yukleniyor...
set PLAYWRIGHT_BROWSERS_PATH=F:\medajan\playwright_browsers
if not exist "%PLAYWRIGHT_BROWSERS_PATH%" mkdir "%PLAYWRIGHT_BROWSERS_PATH%"
venv\Scripts\playwright.exe install chromium
if %errorlevel% neq 0 (
    echo [!!] Playwright kurulumu basarisiz. WhatsApp/TikTok otomasyonu calismaayabilir.
    echo      Elle kurmak icin: venv\Scripts\playwright.exe install chromium
)

echo.
echo [5/5] Dizinler olusturuluyor...
if not exist "data"              mkdir data
if not exist "logs"              mkdir logs
if not exist "media\posts"       mkdir media\posts
if not exist "media\stories"     mkdir media\stories
if not exist "config"            mkdir config

echo.
echo  ══════════════════════════════════
echo  Kurulum tamamlandi!
echo.
echo  Programi baslatmak icin:
echo    start.bat        → GUI + Web panel
echo    start_web.bat    → Sadece web panel
echo.
echo  Web panel: http://localhost:8000
echo  ══════════════════════════════════
echo.
pause
