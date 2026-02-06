# PropKit 完整流程使用指南

## 🚀 快速开始

### 方法一：一键全流程测试（推荐）

**双击运行：`运行全流程测试.bat`**

这个脚本会自动：
1. ✅ 关闭旧进程
2. ✅ 启动 Cloudflared 隧道
3. ✅ 启动 Python 后端
4. ✅ 等待服务就绪
5. ✅ 自动打开浏览器
6. ✅ 显示测试说明

### 方法二：使用批处理文件

**双击运行：`全流程测试.bat`**

功能相同，但使用批处理脚本实现。

---

## 📋 完整流程说明

### 1. 服务启动阶段

**自动执行：**
- 清理旧进程（cloudflared.exe, python.exe）
- 启动 Cloudflared 隧道（最小化窗口）
- 启动 Python 后端（新窗口）
- 等待 15-30 秒让服务初始化

**验证：**
- Cloudflared 窗口显示 "Connected"
- Python 窗口显示 "🚀 后端已就绪，等待 Cloudflare 隧道连接..."

### 2. 浏览器测试阶段

**自动执行：**
- 打开浏览器
- 访问：https://propkitai.tech/landing.html

**手动操作：**
1. 点击 "Request Access" 按钮
2. 输入测试邮箱（例如：`test_fullflow@example.com`）
3. 点击 "ACTIVATE FREE TRIAL"

### 3. 后端处理阶段

**观察 Python 后端窗口，应该看到：**

```
⚡ [3090] 启动任务: test_fullflow@example.com
  运行 GPU 计算: x64/Debug/CudaRuntime1.exe
  ✅ GPU 计算完成
  运行 JSON 导出: C:\ProgramData\Anaconda3\python.exe export_json.py
  ✅ JSON 导出完成
✅ 同步完成，状态码: 201
```

**时间线：**
- Webhook 调用：立即
- GPU 计算：30-120 秒
- JSON 导出：1-2 秒
- Supabase 上传：1-2 秒

### 4. Dashboard 显示阶段

**自动执行：**
- 浏览器自动跳转到 dashboard
- Dashboard 从 Supabase 读取数据
- 渲染 ECharts 图表

**验证：**
- ✅ 图表正常显示
- ✅ 右上角显示统计信息
- ✅ 数据点正确渲染

---

## 🔧 手动操作流程

如果自动脚本不工作，可以手动执行：

### 步骤 1：启动服务

**窗口 1 - Cloudflared:**
```cmd
cd C:\Users\Administrator\Desktop\baseball\netlify_deploy\netlify_deploy1
cloudflared.exe tunnel --config config.yml run 3090-Home
```

**窗口 2 - Python:**
```cmd
cd C:\Users\Administrator\Desktop\baseball\netlify_deploy\netlify_deploy1
C:\ProgramData\Anaconda3\python.exe main.py
```

### 步骤 2：等待服务就绪

等待 15-30 秒，直到：
- Cloudflared 显示 "Connected"
- Python 显示 "Uvicorn running on http://127.0.0.1:8000"

### 步骤 3：打开浏览器

访问：**https://propkitai.tech/landing.html**

### 步骤 4：执行测试

1. 点击 "Request Access"
2. 输入邮箱
3. 点击 "ACTIVATE FREE TRIAL"
4. 观察后端窗口
5. 等待跳转到 dashboard

---

## ✅ 成功标准

完整流程成功的标志：

- [x] 服务正常启动
- [x] 浏览器自动打开
- [x] Landing page 正常显示
- [x] 可以点击按钮并输入邮箱
- [x] 提交后看到激活提示
- [x] Python 后端开始处理
- [x] GPU 计算完成
- [x] JSON 导出完成
- [x] 数据上传成功（状态码 201）
- [x] 自动跳转到 dashboard
- [x] Dashboard 显示图表和数据

---

## 🐛 故障排查

### 问题 1：服务启动失败

**检查：**
- cloudflared.exe 是否存在
- config.yml 是否存在
- Python 环境是否正确

**解决：**
- 查看错误信息
- 检查文件路径
- 运行诊断脚本

### 问题 2：浏览器无法访问

**检查：**
- Cloudflared 是否显示 "Connected"
- 域名是否正确
- 网络连接是否正常

**解决：**
- 等待更长时间
- 检查 Cloudflared 窗口
- 手动访问测试

### 问题 3：提交后无反应

**检查：**
- Python 后端窗口是否有错误
- 浏览器控制台（F12）是否有错误
- API 是否可访问

**解决：**
- 查看后端日志
- 检查网络请求
- 验证服务状态

### 问题 4：Dashboard 无数据

**检查：**
- Supabase 中是否有数据
- 邮箱地址是否匹配
- 数据是否已上传

**解决：**
- 等待 GPU 计算完成
- 检查后端日志
- 运行诊断脚本

---

## 📊 测试工具

### 1. 全流程测试
- `运行全流程测试.bat` - Python 自动化版本（推荐）
- `全流程测试.bat` - 批处理版本

### 2. 服务检查
- `check_services.bat` - 检查服务状态
- `verify_flow.ps1` - PowerShell 验证脚本

### 3. 诊断工具
- `diagnose_supabase.py` - 数据库诊断
- `test_local_compute.py` - 本地计算测试
- `test_upload.py` - 上传测试

---

## 📝 测试记录模板

**测试时间：** _______________

**测试邮箱：** _______________

**服务启动：** [ ] 成功 [ ] 失败

**浏览器测试：** [ ] 成功 [ ] 失败

**后端处理：** [ ] 成功 [ ] 失败

**Dashboard 显示：** [ ] 成功 [ ] 失败

**总耗时：** _______________ 秒

**备注：**
_________________________________________________

---

## 🎯 最佳实践

1. **每次测试前清理旧进程**
   - 确保没有残留进程
   - 避免端口冲突

2. **等待服务完全就绪**
   - 至少等待 15 秒
   - 验证服务状态

3. **观察后端日志**
   - 监控处理进度
   - 及时发现错误

4. **使用唯一测试邮箱**
   - 每次使用不同的邮箱
   - 便于追踪测试记录

5. **记录测试结果**
   - 记录成功/失败
   - 记录错误信息
   - 便于问题排查

---

**现在可以开始测试了！运行 `运行全流程测试.bat` 开始完整的端到端测试。**
