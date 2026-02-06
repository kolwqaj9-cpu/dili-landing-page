@echo off
chcp 65001 >nul
echo ========================================
echo PropKit 流程验证
echo ========================================
echo.

cd /d "%~dp0"

echo 正在运行端到端验证脚本...
echo.

C:\ProgramData\Anaconda3\python.exe e2e_full_verification.py

echo.
echo ========================================
pause
