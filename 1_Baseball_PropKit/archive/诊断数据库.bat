@echo off
chcp 65001 >nul
echo ========================================
echo Supabase 数据库诊断工具
echo ========================================
echo.

cd /d "%~dp0"

C:\ProgramData\Anaconda3\python.exe diagnose_supabase.py

echo.
echo ========================================
pause
