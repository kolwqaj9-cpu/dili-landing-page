@echo off
title Netlify Auto Deploy
color 0C
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   Netlify Automatic Deployment
echo ========================================
echo.

cd /d "%~dp0"

REM Check if Netlify CLI is installed
echo [1/4] Checking Netlify CLI...
netlify --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Netlify CLI not installed
    echo.
    echo Installing Netlify CLI...
    call npm install -g netlify-cli
    if %ERRORLEVEL% NEQ 0 (
        echo [FAIL] Failed to install Netlify CLI
        echo Please install manually: npm install -g netlify-cli
        pause
        exit /b 1
    )
    echo [OK] Netlify CLI installed
) else (
    echo [OK] Netlify CLI is installed
)

echo.
echo [2/4] Checking login status...
netlify status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Not logged in, please login...
    netlify login
    if %ERRORLEVEL% NEQ 0 (
        echo [FAIL] Login failed
        pause
        exit /b 1
    )
) else (
    echo [OK] Already logged in
)

echo.
echo [3/4] Preparing deployment...
echo   Current directory: %CD%
echo   Files to deploy: *.html, *.toml, etc.

echo.
echo [4/4] Deploying to Netlify...
echo   This will deploy to: https://propkitai.tech
echo.

netlify deploy --prod

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Deployment Successful!
    echo ========================================
    echo.
    echo Your site is live at: https://propkitai.tech
    echo.
) else (
    echo.
    echo ========================================
    echo   Deployment Failed!
    echo ========================================
    echo.
    echo Please check the error messages above
    echo.
)

pause
