# 部署检查清单

## ✅ 已完成的配置

### 1. API 地址配置
所有 HTML 文件已配置为使用 `api.propkitai.tech`：
- ✅ `purchase_stats.html` - 使用 `https://api.propkitai.tech`
- ✅ `checkout.html` - 使用 `https://api.propkitai.tech/api/webhook`
- ✅ `landing.html` - 使用 `https://api.propkitai.tech/api/webhook`
- ✅ `signals_dashboard.html` - 使用 `https://api.propkitai.tech`

### 2. Cloudflare Tunnel 配置
- ✅ `config.yml` 已配置：`api.propkitai.tech -> localhost:8000`

### 3. 代码已上传
- ✅ 所有文件已推送到 GitHub
- ✅ 演示模式已启用（零 GPU 消耗）
- ✅ 购买统计功能已实现

## ⚠️ 部署前必须确认

### 1. 后端服务运行状态
```bash
# 必须运行以下服务：
python main.py
```

### 2. Cloudflare Tunnel 运行状态
```bash
# 必须运行隧道：
cloudflared tunnel --config config.yml run 3090-Home
```

### 3. 验证步骤
1. 打开浏览器访问：`https://baseprops.tech/purchase_stats.html`
2. 检查浏览器控制台（F12）是否有错误
3. 确认统计数据能正常显示

## 🔍 故障排查

### 如果统计页面显示 "Error loading statistics"

**可能原因：**
1. 后端未运行 → 检查 `python main.py` 是否在运行
2. Cloudflare Tunnel 未运行 → 检查隧道是否连接
3. Supabase 表未创建 → 执行 `CREATE_PURCHASES_TABLE.sql`
4. API 密钥未配置 → 检查 `.env` 文件

**检查命令：**
```powershell
# 检查后端是否运行
netstat -ano | Select-String ":8000"

# 检查 Cloudflare Tunnel
Get-Process | Where-Object { $_.ProcessName -like "*cloudflared*" }
```

## 📝 重要提醒

⚠️ **保持服务运行：**
- 不要关闭运行 `python main.py` 的窗口
- 不要关闭运行 `cloudflared` 的窗口
- 这两个服务必须持续运行，公网用户才能访问

## 🎯 当前状态

- ✅ 代码已上传到 GitHub
- ✅ API 地址已配置为 `api.propkitai.tech`
- ⚠️ 需要确认后端和隧道是否正在运行
