# 安全配置说明

## API Key 管理

### 问题
前端代码（HTML/JavaScript）是公开的，无法真正隐藏 API Key。如果在前端代码中硬编码 API Key，任何人都可以在浏览器开发者工具中看到。

### 解决方案
使用后端 API 代理，将 API Key 存储在服务器端。

### 配置步骤

1. **设置环境变量（推荐）**

在服务器上设置环境变量：
```bash
# Windows PowerShell
$env:SUPABASE_URL = "https://vlrdiajxxnangawfcgvk.supabase.co"
$env:SUPABASE_KEY = "your-api-key-here"

# Linux/Mac
export SUPABASE_URL="https://vlrdiajxxnangawfcgvk.supabase.co"
export SUPABASE_KEY="your-api-key-here"
```

2. **或者使用配置文件（不提交到 Git）**

创建 `config.local.py`（已在 .gitignore 中）：
```python
SUPABASE_URL = "https://vlrdiajxxnangawfcgvk.supabase.co"
SUPABASE_KEY = "your-api-key-here"
```

然后在 `main.py` 中导入：
```python
try:
    from config.local import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    # 使用默认值（仅用于开发）
    SUPABASE_URL = "https://vlrdiajxxnangawfcgvk.supabase.co"
    SUPABASE_KEY = "your-api-key-here"
```

### 当前实现

- ✅ 前端 `dashboard.html` 通过 `/api/data` 接口获取数据
- ✅ 后端 `main.py` 提供 `/api/data` 接口，使用环境变量或代码中的配置
- ✅ API Key 不再暴露在前端代码中

### 注意事项

1. **不要将 API Key 提交到 Git**
   - 使用 `.gitignore` 排除配置文件
   - 使用环境变量存储敏感信息

2. **定期更换 API Key**
   - 如果 API Key 已经泄露，立即在 Supabase 控制台撤销
   - 生成新的 API Key 并更新环境变量

3. **使用 Row Level Security (RLS)**
   - 在 Supabase 中启用 RLS
   - 限制 API Key 的权限范围
