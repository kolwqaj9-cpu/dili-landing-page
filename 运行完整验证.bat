@echo off
title PropKit Complete Verification
color 0E
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   PropKit Complete Automated Verification
echo ========================================
echo.
echo This will:
echo   1. Check services are running
echo   2. Simulate visitor clicking (free trial, no payment)
echo   3. Wait for CUDA computation
echo   4. Verify computation results
echo   5. Verify dashboard display
echo.
echo ========================================
echo.

cd /d "%~dp0"

REM Selenium is optional - script will work without it
REM If you want browser verification, install: pip install selenium

echo Running complete verification...
echo.

C:\ProgramData\Anaconda3\python.exe 自动化验证完整流程.py

echo.
echo ========================================
pause
