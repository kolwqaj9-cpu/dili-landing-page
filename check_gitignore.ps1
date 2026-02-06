# PowerShell 脚本：在 git add 前检查 .gitignore
# 使用方法：在 git add 前运行 .\check_gitignore.ps1

Write-Host "🔍 检查 .gitignore 规则..." -ForegroundColor Cyan

# 获取暂存区的文件列表
$stagedFiles = git diff --cached --name-only

if ($stagedFiles.Count -eq 0) {
    Write-Host "ℹ️  暂存区为空，无需检查" -ForegroundColor Yellow
    exit 0
}

# 检查每个文件是否应该被忽略
$violations = @()
foreach ($file in $stagedFiles) {
    $shouldIgnore = git check-ignore -q $file
    if ($LASTEXITCODE -eq 0) {
        $rule = git check-ignore -v $file | Select-Object -First 1
        $violations += [PSCustomObject]@{
            File = $file
            Rule = $rule
        }
    }
}

if ($violations.Count -gt 0) {
    Write-Host "`n❌ 发现违反 .gitignore 规则的文件：" -ForegroundColor Red
    foreach ($v in $violations) {
        Write-Host "  文件: $($v.File)" -ForegroundColor Red
        Write-Host "  规则: $($v.Rule)" -ForegroundColor Yellow
    }
    Write-Host "`n请从暂存区移除这些文件：" -ForegroundColor Yellow
    Write-Host "  git reset HEAD <文件路径>" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "✅ 所有文件都符合 .gitignore 规则" -ForegroundColor Green
    exit 0
}
