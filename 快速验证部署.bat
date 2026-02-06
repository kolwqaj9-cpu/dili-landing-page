@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   快速验证部署是否成功
echo ============================================================
echo.

echo [1] 检查部署的 landing.html...
C:\ProgramData\Anaconda3\python.exe -c "import requests; r=requests.get('https://propkitai.tech/landing.html', timeout=10); print('  状态码:', r.status_code); print('  包含 VERSION 3.0:', 'VERSION 3.0' in r.text); print('  包含 API 配置:', 'api.propkitai.tech/api/webhook' in r.text)"

echo.
echo [2] 检查部署的 index.html...
C:\ProgramData\Anaconda3\python.exe -c "import requests; r=requests.get('https://propkitai.tech/', timeout=10); print('  状态码:', r.status_code); print('  包含 VERSION 3.0:', 'VERSION 3.0' in r.text)"

echo.
echo ============================================================
echo   验证结果
echo ============================================================
echo.
echo 如果看到 "包含 VERSION 3.0: True" = 部署成功
echo 如果看到 "包含 VERSION 3.0: False" = 部署失败或未发布
echo.
echo 如果部署成功但连接失败，需要启动后端服务:
echo   .\start_services.ps1
echo.
pause
