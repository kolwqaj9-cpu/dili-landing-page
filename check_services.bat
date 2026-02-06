@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo PropKit Service Status Check
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Checking Cloudflared...
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | find /I "cloudflared.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Cloudflared is running
) else (
    echo [FAIL] Cloudflared is NOT running
    echo Run: start_services.ps1
)

echo.
echo [2] Checking Python Backend...
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python backend is running
) else (
    echo [FAIL] Python backend is NOT running
    echo Run: start_services.ps1
)

echo.
echo [3] Checking Files...
if exist "landing.html" (echo [OK] landing.html) else (echo [FAIL] landing.html)
if exist "dashboard.html" (echo [OK] dashboard.html) else (echo [FAIL] dashboard.html)
if exist "main.py" (echo [OK] main.py) else (echo [FAIL] main.py)

echo.
echo ========================================
echo Ready for browser test!
echo Visit: https://propkitai.tech/landing.html
echo ========================================
pause
