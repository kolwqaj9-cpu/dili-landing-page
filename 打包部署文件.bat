@echo off
title Package for Netlify
color 0B
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   Package Files for Netlify Deployment
echo ========================================
echo.

cd /d "%~dp0"

set PACKAGE_DIR=netlify_deploy_package
set PACKAGE_ZIP=netlify_deploy_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.zip

REM Clean old package
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
if exist "%PACKAGE_ZIP%" del "%PACKAGE_ZIP%"

echo [1/3] Creating package directory...
mkdir "%PACKAGE_DIR%"

echo [2/3] Copying files...
echo   Copying HTML files...
copy /Y *.html "%PACKAGE_DIR%\" >nul 2>&1

echo   Copying configuration files...
copy /Y netlify.toml "%PACKAGE_DIR%\" >nul 2>&1
if exist _redirects copy /Y _redirects "%PACKAGE_DIR%\" >nul 2>&1

echo   Copying other web files...
if exist *.css copy /Y *.css "%PACKAGE_DIR%\" >nul 2>&1
if exist *.js copy /Y *.js "%PACKAGE_DIR%\" >nul 2>&1

echo [OK] Files copied

echo.
echo [3/3] Creating ZIP archive...
powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath '%PACKAGE_ZIP%' -Force" >nul 2>&1

if exist "%PACKAGE_ZIP%" (
    echo [OK] Package created: %PACKAGE_ZIP%
    echo.
    echo ========================================
    echo   Package Ready for Manual Upload
    echo ========================================
    echo.
    echo File: %PACKAGE_ZIP%
    echo.
    echo Instructions:
    echo   1. Go to https://app.netlify.com
    echo   2. Select your site
    echo   3. Drag and drop the ZIP file
    echo   4. Or extract and drag the folder
    echo.
    echo Opening package location...
    explorer /select,"%CD%\%PACKAGE_ZIP%"
) else (
    echo [FAIL] Failed to create package
)

echo.
pause
