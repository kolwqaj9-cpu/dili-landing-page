@echo off
title Quick Deploy and Publish
color 0A
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo   Quick Deploy to Netlify
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Uploading files...
C:\ProgramData\Anaconda3\python.exe deploy_to_netlify.py

echo.
echo ========================================
echo   Next Steps
echo ========================================
echo.
echo If deployment shows success but site is not updated:
echo.
echo 1. Go to Netlify Dashboard:
echo    https://app.netlify.com
echo.
echo 2. Select your site (propkitai.tech)
echo.
echo 3. Go to "Deploys" tab
echo.
echo 4. Find the latest deploy (should be at the top)
echo.
echo 5. Click "Publish deploy" button (if it shows as draft)
echo.
echo 6. Wait 1-2 minutes for CDN to update
echo.
echo 7. Clear browser cache (Ctrl+F5) or use incognito window
echo.
echo ========================================
pause
