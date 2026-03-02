@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   快速验证完整流程
echo ============================================================
echo.
echo [1/3] 检查服务状态...
C:\ProgramData\Anaconda3\python.exe check_site_status.py
echo.
echo [2/3] 检查网站内容...
C:\ProgramData\Anaconda3\python.exe -c "import requests; r=requests.get('https://propkitai.tech/'); print('主页内容检查:'); print('  - 包含 PropKit Analytics:', 'PropKit Analytics' in r.text); print('  - 包含旧内容 Listing Magic:', 'Listing Magic' in r.text)"
echo.
echo [3/3] 如果需要完整端到端验证，运行:
echo   C:\ProgramData\Anaconda3\python.exe e2e_full_verification.py
echo.
echo ============================================================
pause
