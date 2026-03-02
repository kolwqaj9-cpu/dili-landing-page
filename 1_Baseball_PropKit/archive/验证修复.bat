@echo off
chcp 65001 >nul
echo ========================================
echo 验证数据库修复
echo ========================================
echo.
echo SQL 已执行成功！
echo 现在验证修复是否生效...
echo.

cd /d "%~dp0"

C:\ProgramData\Anaconda3\python.exe diagnose_supabase.py

echo.
echo ========================================
echo 如果所有检查都通过，可以运行完整验证：
echo   C:\ProgramData\Anaconda3\python.exe e2e_full_verification.py
echo ========================================
pause
