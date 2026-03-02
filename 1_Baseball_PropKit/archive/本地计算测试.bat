@echo off
chcp 65001 >nul
echo ========================================
echo PropKit 本地计算测试
echo ========================================
echo.
echo 此脚本将直接运行 GPU 计算和 JSON 生成
echo 不通过 webhook，用于测试本地计算流程
echo.

cd /d "%~dp0"

C:\ProgramData\Anaconda3\python.exe test_local_compute.py

echo.
echo ========================================
pause
