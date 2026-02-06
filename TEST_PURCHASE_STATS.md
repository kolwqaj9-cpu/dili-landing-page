# 购买统计功能测试指南

## 📋 测试步骤

### 1. 启动后端服务

在项目根目录运行：
```bash
python main.py
```

或者双击运行：
```
一键启动.bat
```

等待看到以下消息：
```
🚀 [INFRA] PropKit Dedicated Tensor Node initialized (PID: xxxx)
📡 [INFRA] Listening on port 8000 | Synchronizing with GPU Accelerated Backbone...
```

### 2. 运行测试脚本

在另一个终端窗口运行：
```powershell
.\test_purchase_simulation.ps1
```

### 3. 预期结果

测试脚本会：
1. ✅ 获取初始统计数据
2. ✅ 模拟 5 个购买意向请求
3. ✅ 等待 3 秒让数据同步
4. ✅ 再次查询统计，确认数据已更新

**成功标志：**
- 总购买意图数增加 5
- 今日购买意图数增加 5
- 能看到最近 5 条购买记录

### 4. 手动测试（可选）

也可以通过浏览器访问：
- 统计页面：`http://localhost:8000/purchase_stats.html`
- 统计 API：`http://localhost:8000/api/stats/purchases`

## 🔍 验证要点

1. **购买记录写入**：检查后端日志是否有 "📊 [STATS] Purchase intent recorded"
2. **统计数据更新**：总购买意图数应该增加
3. **数据持久化**：重启后端后，统计数据应该仍然存在（从 Supabase 读取）

## ⚠️ 注意事项

- 确保 Supabase 的 `purchases` 表已创建
- 确保 `.env` 文件中的 `SUPABASE_SERVICE_ROLE_KEY` 配置正确
- 如果测试失败，检查后端日志中的错误信息
