# PropKit 快速启动指南

## 📋 项目概述

PropKit 是一个基于 GPU 计算的预测分析平台，包含三个版本：
- **Alpha**: 机构研究平台 (landing.html → dashboard.html)
- **Signals**: 市场智能平台 (signals_landing.html → signals_dashboard.html)
- **Terminal**: API 开发者平台 (terminal_landing.html → terminal_dashboard.html)

## 🚀 快速启动

### 方法一：使用自动化脚本（推荐）

1. **启动所有服务**
   ```powershell
   .\start_services.ps1
   ```
   这会自动启动：
   - Cloudflared 隧道
   - Python 后端（使用 Anaconda Python）

2. **验证流程**
   ```powershell
   C:\ProgramData\Anaconda3\python.exe e2e_full_verification.py
   ```

### 方法二：手动启动

**终端 1 - Cloudflared 隧道：**
```powershell
cd C:\Users\Administrator\Desktop\baseball\netlify_deploy\netlify_deploy1
cloudflared tunnel --config config.yml run 3090-Home
```

**终端 2 - Python 后端：**
```powershell
cd C:\Users\Administrator\Desktop\baseball\netlify_deploy\netlify_deploy1
C:\ProgramData\Anaconda3\python.exe main.py
```

## 🔄 完整流程验证

### 1. 启动服务
确保两个服务都在运行：
- ✅ Cloudflared 隧道（映射 api.propkitai.tech → localhost:8000）
- ✅ Python FastAPI 后端（监听 localhost:8000）

### 2. 测试 Landing Page
访问：https://propkitai.tech/landing.html

### 3. 触发流程
1. 点击 "Request Access" 按钮
2. 输入邮箱地址
3. 点击 "ACTIVATE FREE TRIAL"

### 4. 系统处理流程
```
用户点击 → Webhook API (api.propkitai.tech/api/webhook)
         → Python 后端接收 (main.py)
         → 启动 GPU 计算 (CudaRuntime1.exe)
         → 格式转换 (export_json.py)
         → 上传到 Supabase
         → 跳转到 Dashboard
         → Dashboard 从 Supabase 读取数据并渲染
```

### 5. 验证结果
Dashboard 会自动：
- 从 Supabase 读取数据
- 渲染 ECharts 图表
- 显示分析结果

## 🧪 端到端验证

运行完整验证脚本：
```powershell
C:\ProgramData\Anaconda3\python.exe e2e_full_verification.py
```

验证脚本会检查：
- ✅ 必要文件是否存在
- ✅ Cloudflared 和 Python 服务是否运行
- ✅ Webhook API 是否可访问
- ✅ 数据是否正确生成并上传到 Supabase
- ✅ 提供测试邮箱和 Dashboard 链接

## 📦 Netlify 自动化部署

### 方法一：使用 Netlify CLI（推荐）

1. **安装 Netlify CLI**
   ```powershell
   npm install -g netlify-cli
   ```

2. **登录 Netlify**
   ```powershell
   netlify login
   ```

3. **部署**
   ```powershell
   .\deploy_netlify.ps1
   ```
   或手动：
   ```powershell
   netlify deploy --prod
   ```

### 方法二：Git 自动部署（最佳实践）

1. **初始化 Git 仓库**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **连接 Netlify**
   - 访问 https://app.netlify.com
   - 添加新站点 → 从 Git 导入
   - 选择你的仓库
   - 设置构建命令：`echo "No build required"`
   - 设置发布目录：`.`

3. **自动部署**
   - 每次 `git push` 都会自动触发部署
   - 无需手动拖拽文件

## 📁 项目结构

```
netlify_deploy1/
├── landing.html              # Alpha 着陆页
├── dashboard.html            # Alpha 仪表板
├── signals_landing.html      # Signals 着陆页
├── signals_dashboard.html    # Signals 仪表板
├── terminal_landing.html     # Terminal 着陆页
├── terminal_dashboard.html   # Terminal 仪表板
├── index.html                # 主页（文件索引）
├── main.py                   # FastAPI 后端
├── export_json.py            # JSON 转换脚本
├── config.yml                # Cloudflared 配置
├── netlify.toml              # Netlify 配置
├── start_services.ps1        # 启动服务脚本
├── deploy_netlify.ps1        # 部署脚本
├── verify_flow.ps1           # 验证脚本
└── e2e_full_verification.py  # 端到端验证脚本
```

## 🔧 技术栈

- **前端**: HTML + Tailwind CSS + ECharts
- **后端**: FastAPI (Python)
- **数据库**: Supabase (PostgreSQL)
- **隧道**: Cloudflared
- **部署**: Netlify
- **GPU 计算**: CUDA (RTX 3090)

## 📝 重要提示

1. **使用 Anaconda Python**
   - 所有 Python 脚本建议使用：`C:\ProgramData\Anaconda3\python.exe`
   - 确保已安装所需依赖：`fastapi`, `uvicorn`, `requests`, `pandas`

2. **Cloudflared 配置**
   - 确保 `config.yml` 中的隧道 ID 正确
   - 确保域名 `api.propkitai.tech` 已正确配置

3. **Supabase 配置**
   - 确保 `main.py` 中的 Supabase URL 和 Key 正确
   - 确保 `reports` 表已创建，包含字段：
     - `user_email` (text)
     - `data_payload` (jsonb)
     - `created_at` (timestamp)

4. **GPU 计算**
   - 确保 `CudaRuntime1.exe` 可执行
   - 确保 `sniper_results.bin` 和 `mlb_full_physics_vectors.csv` 存在

## 🐛 故障排除

### API 无法访问
- 检查 Cloudflared 是否运行
- 检查 `config.yml` 配置是否正确
- 检查域名 DNS 设置

### 数据未生成
- 检查 Python 后端日志
- 检查 GPU 计算是否完成
- 检查 `export_json.py` 是否执行成功
- 检查 Supabase 连接

### Dashboard 无数据
- 检查 Supabase 中是否有对应邮箱的记录
- 检查 Dashboard 中的 Supabase 配置
- 检查浏览器控制台错误

## 📞 支持

如有问题，请检查：
1. 服务状态：`.\verify_flow.ps1`
2. 端到端验证：`C:\ProgramData\Anaconda3\python.exe e2e_full_verification.py`
3. 查看各服务的日志输出
