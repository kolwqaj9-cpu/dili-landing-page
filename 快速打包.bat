@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   创建 Netlify 部署包
echo ============================================================
echo.
C:\ProgramData\Anaconda3\python.exe create_deploy_zip.py
echo.
echo ============================================================
pause
