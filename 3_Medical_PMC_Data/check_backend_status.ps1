# 检查后端服务状态
Write-Host ""
Write-Host "检查后端服务状态..." -ForegroundColor Cyan
Write-Host ""

$port8000 = netstat -ano | Select-String ":8000"

if ($port8000) {
    Write-Host "✅ 后端服务正在运行 (端口 8000)" -ForegroundColor Green
    Write-Host ""
    Write-Host "可以运行测试脚本：" -ForegroundColor Yellow
    Write-Host "   .\test_purchase_simulation.ps1" -ForegroundColor White
} else {
    Write-Host "❌ 后端服务未运行" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先启动后端：" -ForegroundColor Yellow
    Write-Host "   python main.py" -ForegroundColor White
    Write-Host ""
    Write-Host "或者运行：" -ForegroundColor Yellow
    Write-Host "   一键启动.bat" -ForegroundColor White
}

Write-Host ""
