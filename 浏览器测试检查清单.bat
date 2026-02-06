@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo PropKit Browser Test Checklist
echo ========================================
echo.

cd /d "%~dp0"

echo [Check 1] Service Status...
echo.

tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | find /I "cloudflared.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Cloudflared is running
) else (
    echo [FAIL] Cloudflared is NOT running
    echo        Please run: start_services.ps1 or yi_jian_qi_dong.bat
)

tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python backend is running
) else (
    echo [FAIL] Python backend is NOT running
    echo        Please run: start_services.ps1 or yi_jian_qi_dong.bat
)

echo.
echo [Check 2] API Connection...
echo.

powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://api.propkitai.tech/api/webhook' -Method GET -TimeoutSec 5 -ErrorAction Stop; Write-Host '[OK] API is accessible (Status:' $response.StatusCode ')' } catch { Write-Host '[WARN] API test failed (may be normal, needs POST request)' }"

echo.
echo [Check 3] Required Files...
echo.

if exist "landing.html" (
    echo [OK] landing.html
) else (
    echo [FAIL] landing.html missing
)

if exist "dashboard.html" (
    echo [OK] dashboard.html
) else (
    echo [FAIL] dashboard.html missing
)

if exist "main.py" (
    echo [OK] main.py
) else (
    echo [FAIL] main.py missing
)

echo.
echo ========================================
echo Test Steps:
echo.
echo 1. Open browser
echo 2. Visit: https://propkitai.tech/landing.html
echo 3. Click "Request Access" button
echo 4. Enter email and click "ACTIVATE FREE TRIAL"
echo 5. Watch Python backend window for logs
echo 6. Wait for auto redirect to dashboard
echo 7. Verify dashboard shows data
echo.
echo For details, see: browser_complete_test.md
echo ========================================
pause
