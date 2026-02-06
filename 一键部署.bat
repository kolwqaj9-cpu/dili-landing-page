@echo off
title One-Click Netlify Deploy
color 0A
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   One-Click Netlify Deployment
echo ========================================
echo.
echo Automatically deploying to Netlify...
echo Site: https://propkitai.tech
echo.
echo ========================================
echo.

cd /d "%~dp0"

C:\ProgramData\Anaconda3\python.exe 自动上传到Netlify.py

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
    echo   Deployment Failed
    echo ========================================
    echo.
    echo Please check the error messages above
    echo.
)

pause
