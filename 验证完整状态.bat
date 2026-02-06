@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   验证完整状态
echo ============================================================
echo.
echo [1] 网站部署状态...
C:\ProgramData\Anaconda3\python.exe check_site_status.py
echo.
echo [2] 后端服务状态...
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | findstr cloudflared >nul && echo   [OK] Cloudflared 运行中 || echo   [FAIL] Cloudflared 未运行
tasklist /FI "IMAGENAME eq python.exe" 2>nul | findstr python >nul && echo   [OK] Python 后端运行中 || echo   [FAIL] Python 后端未运行
echo.
echo [3] API 连接测试...
C:\ProgramData\Anaconda3\python.exe -c "import requests; r=requests.get('https://api.propkitai.tech/api/webhook', timeout=5); print('  API 状态码:', r.status_code); print('  状态:', '正常' if r.status_code < 500 else '服务未就绪')" 2>nul
echo.
echo ============================================================
echo   总结
echo ============================================================
echo.
echo 如果后端服务未运行，请执行:
echo   .\start_services.ps1
echo.
echo 如果网站显示旧内容，请:
echo   1. 清除浏览器缓存 (Ctrl+F5)
echo   2. 或使用无痕窗口
echo.
pause
