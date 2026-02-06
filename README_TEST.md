# 自动化测试说明

## 测试脚本：check_my_biz.py

这个脚本用于验证后端 API 和前端页面的数据一致性。

## 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

## 运行测试

```bash
python check_my_biz.py
```

## 测试流程

1. **访问 API**：直接访问 `https://baseprops.vercel.app/api/stats/purchases`
2. **检查数据**：
   - 如果 `total_intents` 为 0：显示红色警告
   - 如果 `total_intents` >= 1：显示绿色成功消息
3. **对比前端**：访问 `https://baseprops.tech/purchase_stats.html`，对比显示的数字

## 输出说明

- ✅ 绿色：测试通过
- ❌ 红色：测试失败或错误
- ⚠️ 黄色：警告信息
- ℹ️ 蓝色：信息提示

## 故障排查

### 如果 API 请求超时
- 检查 Vercel 服务是否在线
- 检查网络连接
- 确认 API URL 是否正确

### 如果 API 返回 0 条数据
- 检查 Vercel 环境变量是否配置正确
- 确认已重新部署（Redeploy）
- 检查 Supabase Service Role Key 是否正确

### 如果前端数据不一致
- 前端可能使用了 localStorage 后备数据
- 检查前端代码是否正确调用 API
