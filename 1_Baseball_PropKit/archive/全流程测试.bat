@echo off
title PropKit Full Flow Test
color 0B
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   PropKit Full Flow Test
echo ========================================
echo.
echo This script will:
echo   1. Start all services
echo   2. Wait for services to be ready
echo   3. Open browser for testing
echo   4. Monitor backend logs
echo.
echo ========================================
echo.

cd /d "%~dp0"

REM Step 1: Kill existing processes
echo [Step 1/5] Cleaning up old processes...
taskkill /F /IM cloudflared.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Cleanup done
echo.

REM Step 2: Start Cloudflared
echo [Step 2/5] Starting Cloudflared Tunnel...
start "Cloudflared Tunnel" /MIN cmd /c "cd /d %~dp0 && cloudflared.exe tunnel --config config.yml run 3090-Home"
timeout /t 5 /nobreak >nul
echo [OK] Cloudflared started
echo.

REM Step 3: Start Python Backend
echo [Step 3/5] Starting Python Backend...
start "Python Backend" cmd /k "cd /d %~dp0 && C:\ProgramData\Anaconda3\python.exe main.py"
timeout /t 5 /nobreak >nul
echo [OK] Python backend started
echo.

REM Step 4: Wait for services to initialize
echo [Step 4/5] Waiting for services to initialize...
echo    Please wait 15 seconds...
for /L %%i in (15,-1,1) do (
    echo    Starting in %%i seconds...
    timeout /t 1 /nobreak >nul
)
echo [OK] Services should be ready now
echo.

REM Step 5: Verify services
echo [Step 5/5] Verifying services...
tasklist | findstr /I "cloudflared.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Cloudflared is running
) else (
    echo [FAIL] Cloudflared is NOT running
)

tasklist | findstr /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python backend is running
) else (
    echo [FAIL] Python backend is NOT running
)

echo.
echo ========================================
echo   Services Ready!
echo ========================================
echo.
echo Opening browser...
echo.
start https://propkitai.tech/landing.html
timeout /t 2 /nobreak >nul

echo ========================================
echo   Test Instructions
echo ========================================
echo.
echo 1. In the browser:
echo    - Click "Request Access" button
echo    - Enter email address
echo    - Click "ACTIVATE FREE TRIAL"
echo.
echo 2. Watch the Python Backend window:
echo    - You should see GPU computation starting
echo    - Wait for "同步完成" message
echo.
echo 3. Browser will auto-redirect to dashboard
echo    - Check if chart is displayed
echo    - Verify data statistics
echo.
echo ========================================
echo.
echo Services are running in background windows.
echo Close those windows to stop services.
echo.
echo Press any key to exit this window...
pause >nul
