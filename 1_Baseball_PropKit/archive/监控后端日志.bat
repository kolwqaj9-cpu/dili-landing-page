@echo off
chcp 65001 >nul
echo ========================================
echo 监控 Python 后端日志
echo ========================================
echo.
echo 此窗口将实时显示后端处理日志
echo 请在另一个窗口运行服务，然后在此窗口查看日志
echo.
echo 按 Ctrl+C 停止监控
echo ========================================
echo.

cd /d "%~dp0"

:loop
echo [%date% %time%] 检查后端状态...
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Python 后端正在运行
) else (
    echo ❌ Python 后端未运行
    echo 请先启动后端服务
)

timeout /t 5 /nobreak >nul
goto loop
