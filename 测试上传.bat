@echo off
chcp 65001 >nul
echo ========================================
echo Supabase 上传测试
echo ========================================
echo.
echo 此脚本将测试将本地 JSON 文件上传到 Supabase
echo.

cd /d "%~dp0"

C:\ProgramData\Anaconda3\python.exe test_upload.py

echo.
echo ========================================
pause
