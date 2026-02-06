@echo off
chcp 65001 >nul
echo ========================================
echo PropKit 完整测试流程
echo ========================================
echo.
echo 此脚本将按顺序执行：
echo  1. 本地计算测试
echo  2. 上传测试
echo  3. 端到端验证
echo.

cd /d "%~dp0"

echo.
echo [步骤 1/3] 本地计算测试...
echo ========================================
C:\ProgramData\Anaconda3\python.exe test_local_compute.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 本地计算测试失败，停止测试
    pause
    exit /b 1
)

echo.
echo [步骤 2/3] 上传测试...
echo ========================================
C:\ProgramData\Anaconda3\python.exe test_upload.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  上传测试失败，但继续端到端验证...
)

echo.
echo [步骤 3/3] 端到端验证...
echo ========================================
C:\ProgramData\Anaconda3\python.exe e2e_full_verification.py

echo.
echo ========================================
echo 完整测试流程结束
echo ========================================
pause
