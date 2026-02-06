@echo off
chcp 65001 >nul
echo ========================================
echo PropKit 一键启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 启动 Cloudflared 隧道...
start "Cloudflared Tunnel" cmd /k "cloudflared.exe tunnel --config config.yml run 3090-Home"
timeout /t 3 /nobreak >nul

echo [2/2] 启动 Python 后端...
start "Python Backend" cmd /k "C:\ProgramData\Anaconda3\python.exe main.py"

echo.
echo ========================================
echo 服务启动完成！
echo.
echo 两个窗口已打开：
echo   - Cloudflared 隧道窗口
echo   - Python 后端窗口
echo.
echo 现在可以：
echo   1. 访问 https://propkitai.tech/landing.html 测试
echo   2. 运行验证脚本检查状态
echo.
echo 关闭窗口即可停止服务
echo ========================================
pause
