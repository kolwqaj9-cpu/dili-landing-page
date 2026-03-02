# 启动所有服务的脚本
# 自动启动 cloudflared 和 python 后端

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动 PropKit 服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "C:\Users\Administrator\Desktop\baseball\netlify_deploy\netlify_deploy1"
Set-Location $projectPath

# 检查 cloudflared 是否存在
if (-not (Test-Path "cloudflared.exe")) {
    Write-Host "  ❌ cloudflared.exe 未找到" -ForegroundColor Red
    exit 1
}

# 检查 config.yml 是否存在
if (-not (Test-Path "config.yml")) {
    Write-Host "  ❌ config.yml 未找到" -ForegroundColor Red
    exit 1
}

Write-Host "[1/2] 启动 Cloudflared 隧道..." -ForegroundColor Yellow
Start-Process -FilePath ".\cloudflared.exe" -ArgumentList "tunnel", "--config", "config.yml", "run", "3090-Home" -WindowStyle Minimized
Start-Sleep -Seconds 2

$cloudflaredProcess = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
if ($cloudflaredProcess) {
    Write-Host "  ✅ Cloudflared 已启动 (PID: $($cloudflaredProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Cloudflared 启动可能失败，请检查" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/2] 启动 Python 后端..." -ForegroundColor Yellow

# 使用 Anaconda Python
$anacondaPython = "C:\ProgramData\Anaconda3\python.exe"
$systemPython = "python"

# 检查 Anaconda Python
if (Test-Path $anacondaPython) {
    $pythonExe = $anacondaPython
    try {
        $pythonVersion = & $pythonExe --version 2>&1
        Write-Host "  使用 Anaconda Python: $pythonVersion" -ForegroundColor Gray
    } catch {
        Write-Host "  ⚠️  Anaconda Python 检查失败，尝试系统 Python" -ForegroundColor Yellow
        $pythonExe = $systemPython
    }
} else {
    Write-Host "  ⚠️  Anaconda Python 未找到，使用系统 Python" -ForegroundColor Yellow
    $pythonExe = $systemPython
    try {
        $pythonVersion = & $pythonExe --version 2>&1
        Write-Host "  Python 版本: $pythonVersion" -ForegroundColor Gray
    } catch {
        Write-Host "  ❌ Python 未安装或不在 PATH 中" -ForegroundColor Red
        exit 1
    }
}

# 检查 main.py
if (-not (Test-Path "main.py")) {
    Write-Host "  ❌ main.py 未找到" -ForegroundColor Red
    exit 1
}

# 启动 Python 后端（在新窗口中）
Start-Process $pythonExe -ArgumentList "main.py" -WorkingDirectory $projectPath

Write-Host "  ✅ Python 后端已启动（新窗口）" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服务启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "现在可以:" -ForegroundColor Cyan
Write-Host "  1. 访问 https://propkitai.tech/landing.html 测试流程" -ForegroundColor White
Write-Host "  2. 运行 .\verify_flow.ps1 验证服务状态" -ForegroundColor White
Write-Host ""
Write-Host "停止服务: 关闭对应的命令行窗口" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
