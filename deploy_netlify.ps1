# Netlify 自动化部署脚本
# 使用 Netlify CLI 自动部署，无需手动拖拽

param(
    [string]$SiteId = "",
    [string]$Token = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Netlify Automatic Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Netlify CLI 是否安装
Write-Host "[1/3] Checking Netlify CLI..." -ForegroundColor Yellow
try {
    $netlifyVersion = netlify --version 2>&1
    Write-Host "  [OK] Netlify CLI installed: $netlifyVersion" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Netlify CLI not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Install:" -ForegroundColor Yellow
    Write-Host "    npm install -g netlify-cli" -ForegroundColor White
    Write-Host ""
    exit 1
}

# 检查是否已登录
Write-Host ""
Write-Host "[2/3] Checking login status..." -ForegroundColor Yellow
try {
    $loginStatus = netlify status 2>&1
    if ($loginStatus -match "Logged in") {
        Write-Host "  [OK] Logged in to Netlify" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Not logged in, opening browser..." -ForegroundColor Yellow
        netlify login
    }
} catch {
    Write-Host "  [WARN] Need to login, run: netlify login" -ForegroundColor Yellow
}

# 部署
Write-Host ""
Write-Host "[3/3] Deploying..." -ForegroundColor Yellow

# 检查是否有 netlify.toml
if (-not (Test-Path "netlify.toml")) {
    Write-Host "  [WARN] netlify.toml not found, using default config" -ForegroundColor Yellow
}

# 执行部署
try {
    if ($SiteId) {
        Write-Host "  Using Site ID: $SiteId" -ForegroundColor Gray
        netlify deploy --prod --site=$SiteId
    } else {
        Write-Host "  Auto-detecting site..." -ForegroundColor Gray
        netlify deploy --prod
    }
    
    Write-Host ""
    Write-Host "  [OK] Deployment completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Site URL: https://propkitai.tech" -ForegroundColor Cyan
} catch {
    Write-Host ""
    Write-Host "  [FAIL] Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Manual deployment:" -ForegroundColor Yellow
    Write-Host "    1. Go to https://app.netlify.com" -ForegroundColor White
    Write-Host "    2. Select your site" -ForegroundColor White
    Write-Host "    3. Drag and drop files" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
