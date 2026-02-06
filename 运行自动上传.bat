@echo off
title Netlify Auto Upload
color 0A
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   Netlify Automatic Upload
echo ========================================
echo.
echo This will automatically upload files to Netlify
echo No drag and drop needed!
echo.
echo ========================================
echo.

cd /d "%~dp0"

C:\ProgramData\Anaconda3\python.exe 自动上传到Netlify.py

echo.
echo ========================================
pause
