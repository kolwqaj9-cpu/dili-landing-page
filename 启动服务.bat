@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo Starting PropKit Services
echo ========================================
echo.

cd /d "%~dp0"

echo [Step 1/2] Starting Cloudflared Tunnel...
echo.
start "Cloudflared" cmd /k "cd /d %~dp0 && cloudflared.exe tunnel --config config.yml run 3090-Home"
timeout /t 3 /nobreak >nul

echo [Step 2/2] Starting Python Backend...
echo.
start "Python Backend" cmd /k "cd /d %~dp0 && C:\ProgramData\Anaconda3\python.exe main.py"

echo.
echo ========================================
echo Services started!
echo.
echo Two windows should have opened:
echo   - Cloudflared Tunnel window
echo   - Python Backend window
echo.
echo Wait 10-15 seconds for services to initialize
echo Then visit: https://propkitai.tech/landing.html
echo.
echo To stop services: Close the windows
echo ========================================
timeout /t 5 /nobreak >nul
