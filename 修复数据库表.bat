@echo off
chcp 65001 >nul
echo ========================================
echo Supabase 表修复指南
echo ========================================
echo.
echo 请按照以下步骤操作：
echo.
echo 1. 打开 Supabase Dashboard
echo    https://app.supabase.com
echo.
echo 2. 选择你的项目
echo.
echo 3. 点击左侧菜单的 "SQL Editor"
echo.
echo 4. 点击 "New query"
echo.
echo 5. 复制并粘贴以下 SQL 语句：
echo.
echo    ALTER TABLE reports 
echo    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
echo.
echo 6. 点击 "Run" 执行
echo.
echo 7. 执行完成后，再次运行诊断脚本验证
echo.
echo ========================================
echo.
echo 或者，你可以直接打开 fix_supabase_table.sql 文件
echo 复制其中的 SQL 语句到 Supabase SQL Editor 执行
echo.
echo ========================================
pause
