# 环境变量配置指南

## 安全配置说明

本项目使用 `.env` 文件存储敏感配置信息（如 Supabase API 密钥），确保这些信息不会被提交到 Git 仓库。

## 设置步骤

### 1. 安装 python-dotenv

```bash
pip install python-dotenv
```

### 2. 创建 .env 文件

在项目根目录创建 `.env` 文件，内容如下：

```env
# Supabase 配置
SUPABASE_URL=https://bmwfnuekfgolwutnffmf.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

### 3. 验证配置

运行项目时，`main.py` 会自动从 `.env` 文件加载环境变量。

如果 `.env` 文件不存在或密钥未设置，程序会显示警告信息。

## 安全注意事项

✅ **已配置的安全措施：**

1. `.env` 文件已在 `.gitignore` 中排除，不会被提交到 Git
2. `main.py` 使用 `python-dotenv` 从环境变量读取配置
3. 代码中不再硬编码敏感信息

⚠️ **重要提醒：**

- **永远不要**将 `.env` 文件提交到 Git
- **永远不要**在代码中硬编码 API 密钥
- 如果密钥泄露，立即在 Supabase 控制台撤销并生成新密钥
- 定期检查 `.gitignore` 确保 `.env` 被正确排除

## 故障排查

### 问题：程序提示找不到 SUPABASE_SERVICE_ROLE_KEY

**解决方案：**
1. 检查 `.env` 文件是否存在于项目根目录
2. 检查 `.env` 文件中的变量名是否正确：`SUPABASE_SERVICE_ROLE_KEY`
3. 确保 `.env` 文件格式正确（每行一个变量，使用 `KEY=VALUE` 格式）

### 问题：密钥仍然暴露在代码中

**解决方案：**
1. 检查 `main.py` 是否已更新为使用 `load_dotenv()`
2. 确保没有在代码中硬编码密钥
3. 如果之前已提交密钥到 Git，需要：
   - 在 Supabase 控制台撤销旧密钥
   - 生成新密钥
   - 更新 `.env` 文件
   - 使用 `git filter-branch` 或 `git filter-repo` 清理 Git 历史
