@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ============================================================
echo   打包所有 HTML 文件
echo ============================================================
echo.

set timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
set zipname=html_files_%timestamp%.zip

echo 正在查找 HTML 文件...
echo.

set count=0
for %%f in (*.html) do (
    echo   [找到] %%f
    set /a count+=1
)

echo.
echo 找到 %count% 个 HTML 文件
echo.

echo 正在创建 ZIP 文件: %zipname%
echo.

powershell -Command "Get-ChildItem -Filter *.html | Compress-Archive -DestinationPath '%zipname%' -Force"

if exist "%zipname%" (
    for %%A in ("%zipname%") do set size=%%~zA
    set /a sizeKB=!size!/1024
    echo ============================================================
    echo   打包完成
    echo ============================================================
    echo.
    echo   文件名: %zipname%
    echo   文件大小: !sizeKB! KB
    echo   包含文件: %count% 个 HTML 文件
    echo   文件位置: %CD%\%zipname%
    echo.
) else (
    echo [错误] 创建 ZIP 文件失败
)

pause
