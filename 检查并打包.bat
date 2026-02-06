@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   检查文件并创建部署包
echo ============================================================
echo.

echo [步骤 1] 检查必要文件...
echo.
if exist index.html (
    echo   [OK] index.html
) else (
    echo   [FAIL] index.html 缺失
)

if exist landing.html (
    echo   [OK] landing.html
) else (
    echo   [FAIL] landing.html 缺失
)

if exist dashboard.html (
    echo   [OK] dashboard.html
) else (
    echo   [FAIL] dashboard.html 缺失
)

if exist signals_landing.html (
    echo   [OK] signals_landing.html
) else (
    echo   [WARN] signals_landing.html 缺失
)

if exist signals_dashboard.html (
    echo   [OK] signals_dashboard.html
) else (
    echo   [WARN] signals_dashboard.html 缺失
)

if exist terminal_landing.html (
    echo   [OK] terminal_landing.html
) else (
    echo   [WARN] terminal_landing.html 缺失
)

if exist terminal_dashboard.html (
    echo   [OK] terminal_dashboard.html
) else (
    echo   [WARN] terminal_dashboard.html 缺失
)

if exist privacy.html (
    echo   [OK] privacy.html
) else (
    echo   [WARN] privacy.html 缺失
)

if exist terms.html (
    echo   [OK] terms.html
) else (
    echo   [WARN] terms.html 缺失
)

if exist netlify.toml (
    echo   [OK] netlify.toml
) else (
    echo   [WARN] netlify.toml 缺失
)

echo.
echo [步骤 2] 创建 ZIP 部署包...
echo.
C:\ProgramData\Anaconda3\python.exe create_deploy_zip.py

echo.
echo ============================================================
echo   完成！
echo ============================================================
echo.
echo ZIP 文件已创建在项目目录中
echo 请拖拽到 Netlify 进行部署
echo.
pause
