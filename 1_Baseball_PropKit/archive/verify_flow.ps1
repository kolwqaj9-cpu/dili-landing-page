# PropKit 流程验证脚本
# 用于验证从 landing page 到 dashboard 的完整流程

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PropKit 流程验证工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查必要的服务是否运行
Write-Host "[1/4] 检查服务状态..." -ForegroundColor Yellow

# 检查 cloudflared 隧道
$cloudflaredProcess = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
if (-not $cloudflaredProcess) {
    Write-Host "  ⚠️  Cloudflared 隧道未运行" -ForegroundColor Red
    Write-Host "  请运行: cloudflared tunnel --config config.yml run 3090-Home" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ Cloudflared 隧道运行中 (PID: $($cloudflaredProcess.Id))" -ForegroundColor Green
}

# 检查 Python 后端
$pythonProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue
if (-not $pythonProcess) {
    Write-Host "  ⚠️  Python 后端未运行" -ForegroundColor Red
    Write-Host "  请运行: C:\ProgramData\Anaconda3\python.exe main.py" -ForegroundColor Yellow
    Write-Host "  或运行: .\start_services.ps1" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ Python 后端运行中 (PID: $($pythonProcess.Id))" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/4] 测试 API 连接..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "https://api.propkitai.tech/api/webhook" -Method POST -Body '{"email":"test@example.com"}' -ContentType "application/json" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✅ API 连接成功 (状态码: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "  ❌ API 连接失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  请确保 cloudflared 隧道正在运行" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/4] 检查必要文件..." -ForegroundColor Yellow

$requiredFiles = @(
    "landing.html",
    "dashboard.html",
    "main.py",
    "config.yml",
    "export_json.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file 缺失" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[4/4] 验证流程说明" -ForegroundColor Yellow
Write-Host ""
Write-Host "完整验证流程:" -ForegroundColor Cyan
Write-Host "  1. 确保两个服务都在运行:" -ForegroundColor White
Write-Host "     - Cloudflared: cloudflared tunnel --config config.yml run 3090-Home" -ForegroundColor Gray
Write-Host "     - Python: C:\ProgramData\Anaconda3\python.exe main.py" -ForegroundColor Gray
Write-Host "     或运行: .\start_services.ps1 (自动启动所有服务)" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 打开浏览器访问: https://propkitai.tech/landing.html" -ForegroundColor White
Write-Host ""
Write-Host "  3. 点击 'Request Access' 按钮" -ForegroundColor White
Write-Host ""
Write-Host "  4. 输入邮箱地址并点击 'ACTIVATE FREE TRIAL'" -ForegroundColor White
Write-Host ""
Write-Host "  5. 系统将:" -ForegroundColor White
Write-Host "     - 调用 webhook API" -ForegroundColor Gray
Write-Host "     - 触发本地 GPU 计算 (CudaRuntime1.exe)" -ForegroundColor Gray
Write-Host "     - 生成 JSON 数据" -ForegroundColor Gray
Write-Host "     - 上传到 Supabase" -ForegroundColor Gray
Write-Host "     - 跳转到 dashboard 显示结果" -ForegroundColor Gray
Write-Host ""
Write-Host "  6. Dashboard 会自动从 Supabase 读取数据并渲染图表" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
