@echo off
title PropKit Quick Start
color 0A
echo.
echo ========================================
echo   PropKit Quick Start
echo ========================================
echo.
echo Starting services...
echo.

cd /d "%~dp0"

REM Kill existing processes
taskkill /F /IM cloudflared.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

REM Start Cloudflared
echo [1/2] Starting Cloudflared...
start "Cloudflared Tunnel" /MIN cmd /c "cd /d %~dp0 && cloudflared.exe tunnel --config config.yml run 3090-Home"
timeout /t 5 /nobreak >nul

REM Start Python
echo [2/2] Starting Python Backend...
start "Python Backend" cmd /k "cd /d %~dp0 && C:\ProgramData\Anaconda3\python.exe main.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo.
echo Two windows opened:
echo   - Cloudflared (minimized)
echo   - Python Backend
echo.
echo Wait 10 seconds, then visit:
echo   https://propkitai.tech/landing.html
echo.
echo Press any key to check service status...
pause >nul

REM Check status
cls
echo.
echo Checking service status...
echo.
tasklist | findstr /I "cloudflared python" | findstr /V "findstr"
echo.
echo If you see cloudflared.exe and python.exe above, services are running!
echo.
pause
