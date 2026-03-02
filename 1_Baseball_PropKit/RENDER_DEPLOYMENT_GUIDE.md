# Render 云端部署指南

## 🎯 目标
将后端从本地电脑迁移到 Render 免费云平台，实现 24/7 在线，无需保持本地电脑开机。

## 📋 部署步骤

### 第一步：在 Render 上创建 Web Service

1. **访问 Render.com**
   - 注册/登录账号（可用 GitHub 账号）
   - 访问：https://render.com

2. **创建新服务**
   - 点击 "New +" → "Web Service"
   - 连接你的 GitHub 仓库（baseprops）

3. **配置服务参数**
   ```
   Name: propkit-backend (或任意名称)
   Region: Oregon (默认即可)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   Instance Type: Free
   ```

4. **配置环境变量**
   在 "Environment Variables" 部分添加：
   ```
   SUPABASE_URL = https://bmwfnuekfgolwutnffmf.supabase.co
   SUPABASE_SERVICE_ROLE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJtd2ZudWVrZmdvbHd1dG5mZm1mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDM1MjIxMywiZXhwIjoyMDg1OTI4MjEzfQ.lYmpk8t9MNiHAqmul6vnT6x_oqCrxcbXN9xgyTKTFPA
   ```

5. **点击 "Create Web Service"**
   - 等待 1-2 分钟部署完成
   - 看到绿色的 "Live" 标志表示成功

### 第二步：获取 Render 地址

部署完成后，你会看到一个类似这样的地址：
```
https://propkit-backend-xxxx.onrender.com
```

**复制这个地址！**

### 第三步：更新前端代码

1. **替换所有 HTML 文件中的占位符**
   
   打开以下文件，将 `YOUR_RENDER_URL` 替换为你的实际 Render 地址：
   - `purchase_stats.html` (第 83 行)
   - `checkout.html` (第 123 行)
   - `landing.html` (第 36 行)
   - `signals_dashboard.html` (第 105 行)

   **示例：**
   ```javascript
   // 修改前
   : 'https://YOUR_RENDER_URL.onrender.com';
   
   // 修改后（假设你的地址是 propkit-backend-abc123）
   : 'https://propkit-backend-abc123.onrender.com';
   ```

2. **提交并推送**
   ```powershell
   git add purchase_stats.html checkout.html landing.html signals_dashboard.html
   git commit -m "Update API endpoints to Render cloud backend"
   git push
   ```

## ✅ 验证部署

1. **检查 Render 服务状态**
   - 在 Render 控制台确认服务显示 "Live"
   - 点击服务地址，应该看到 FastAPI 的自动文档页面

2. **测试 API 端点**
   - 访问：`https://你的地址.onrender.com/api/stats/purchases`
   - 应该返回 JSON 数据（可能为空，但不应报错）

3. **测试前端页面**
   - 访问：`https://baseprops.tech/purchase_stats.html`
   - 应该能正常加载统计数据

## 🎉 完成！

现在你的系统已经完全云端化：
- ✅ 后端运行在 Render（免费，24/7 在线）
- ✅ 前端运行在 GitHub Pages
- ✅ 数据库在 Supabase
- ✅ **你的本地电脑可以关机了！**

## ⚠️ 注意事项

1. **Render 免费版限制**
   - 服务在 15 分钟无活动后会休眠
   - 首次请求可能需要 30-60 秒唤醒
   - 每月有使用时间限制

2. **如果服务休眠**
   - 首次访问会较慢（唤醒时间）
   - 后续请求会正常响应

3. **升级方案**
   - 如果需要 24/7 无休眠，可升级到付费版（$7/月起）
   - 或使用其他免费平台（Railway、Fly.io 等）

## 🔧 故障排查

### 问题：部署失败
- 检查 `requirements.txt` 是否包含所有依赖
- 检查环境变量是否正确配置
- 查看 Render 日志（Logs 标签页）

### 问题：API 返回 500 错误
- 检查 Supabase 密钥是否正确
- 检查 Supabase 表是否已创建
- 查看 Render 日志获取详细错误信息

### 问题：前端无法连接
- 确认 Render 地址是否正确替换
- 检查浏览器控制台（F12）的错误信息
- 确认 Render 服务状态为 "Live"
