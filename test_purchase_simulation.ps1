# 购买意向模拟测试脚本
$API_BASE = "http://localhost:8000"
$WEBHOOK_URL = "$API_BASE/api/webhook"
$STATS_URL = "$API_BASE/api/stats/purchases"

# 测试用户列表
$testUsers = @(
    "alpha.trader@institutional.com",
    "quant.analyst@hedgefund.io",
    "prop.desk@marketmaker.com",
    "research.team@propfirm.net",
    "signal.subscriber@trading.com"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "购买意向模拟测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 先查看初始统计
Write-Host "📊 获取初始统计数据..." -ForegroundColor Yellow
try {
    $initialStats = Invoke-RestMethod -Uri $STATS_URL -Method Get -TimeoutSec 10
    $initialTotal = $initialStats.data.total_intents
    $initialToday = $initialStats.data.today_intents
    Write-Host "   总购买意图数: $initialTotal" -ForegroundColor White
    Write-Host "   今日购买意图数: $initialToday" -ForegroundColor White
    Write-Host "   预估收入: `$$(($initialTotal) * 99)" -ForegroundColor Yellow
    Write-Host ""
} catch {
    Write-Host "   ⚠️ 无法获取初始统计: $_" -ForegroundColor Red
    $initialTotal = 0
    $initialToday = 0
    Write-Host ""
}

# 模拟购买请求
Write-Host "🚀 开始模拟购买意向..." -ForegroundColor Green
Write-Host ""
$successCount = 0

foreach ($email in $testUsers) {
    $body = @{
        email = $email
        source = "Signals_Checkout_Page"
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri $WEBHOOK_URL -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
        Write-Host "✅ $($email.PadRight(45)) Status: $($response.status)" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "❌ $($email.PadRight(45)) Error: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "✅ 成功模拟: $successCount/$($testUsers.Count) 个购买意向" -ForegroundColor Green
Write-Host ""

# 等待数据同步
Write-Host "⏳ 等待 3 秒，让数据同步到数据库..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host ""

# 再次查看统计
Write-Host "📊 更新后的统计数据：" -ForegroundColor Cyan
try {
    $finalStats = Invoke-RestMethod -Uri $STATS_URL -Method Get -TimeoutSec 10
    $finalTotal = $finalStats.data.total_intents
    $finalToday = $finalStats.data.today_intents
    $revenue = $finalTotal * 99
    $increase = $finalTotal - $initialTotal
    
    Write-Host "   总购买意图数: $finalTotal (增加: $increase)" -ForegroundColor White
    Write-Host "   今日购买意图数: $finalToday" -ForegroundColor White
    Write-Host "   预估收入: `$$revenue" -ForegroundColor Yellow
    Write-Host ""
    
    # 显示最近购买记录
    $recent = $finalStats.data.recent_purchases
    if ($recent -and $recent.Count -gt 0) {
        Write-Host "📋 最近购买记录（前 5 条）：" -ForegroundColor Cyan
        $count = [Math]::Min(5, $recent.Count)
        for ($i = 0; $i -lt $count; $i++) {
            $p = $recent[$i]
            $email = $p.user_email
            $amount = $p.amount
            $status = $p.status
            $time = $p.timestamp
            if ($time.Length -gt 19) { $time = $time.Substring(0, 19) }
            Write-Host "   $($i+1). $($email.PadRight(35)) `$$amount  $status  $time" -ForegroundColor Gray
        }
    } else {
        Write-Host "   (暂无最近购买记录)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "✅ 测试完成！统计数据已更新。" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ 获取统计失败: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
