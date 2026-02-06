# Netlify 部署指南

## 🚀 三种部署方式

### 方式一：自动化部署（推荐）⭐

使用 Netlify CLI 自动部署，无需手动操作。

#### 步骤：

1. **安装 Netlify CLI**（如果未安装）
   ```cmd
   npm install -g netlify-cli
   ```

2. **运行自动部署脚本**
   ```cmd
   双击: 自动部署到Netlify.bat
   ```

3. **首次使用需要登录**
   - 脚本会自动打开浏览器
   - 点击 "Authorize" 授权
   - 返回命令行继续

4. **部署完成**
   - 自动上传所有文件
   - 显示部署 URL

#### 优点：
- ✅ 完全自动化
- ✅ 无需手动操作
- ✅ 可以集成到 CI/CD

---

### 方式二：Git 自动部署（最佳实践）⭐⭐⭐

每次 `git push` 自动触发部署。

#### 设置步骤：

1. **初始化 Git 仓库**
   ```cmd
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **推送到 GitHub/GitLab**
   ```cmd
   git remote add origin https://github.com/yourusername/yourrepo.git
   git push -u origin main
   ```

3. **在 Netlify 中连接**
   - 访问 https://app.netlify.com
   - 点击 "Add new site" → "Import an existing project"
   - 选择你的 Git 提供商（GitHub/GitLab）
   - 选择仓库
   - 设置：
     - Build command: `echo "No build required"`
     - Publish directory: `.`
   - 点击 "Deploy site"

4. **完成**
   - 每次 `git push` 都会自动部署
   - 无需任何手动操作

#### 优点：
- ✅ 完全自动化
- ✅ 版本控制
- ✅ 部署历史
- ✅ 回滚功能

---

### 方式三：手动拖拽上传

打包文件后手动上传到 Netlify。

#### 步骤：

1. **打包文件**
   ```cmd
   双击: 打包部署文件.bat
   ```

2. **获取 ZIP 文件**
   - 脚本会创建一个 ZIP 文件
   - 文件名：`netlify_deploy_YYYYMMDD_HHMM.zip`

3. **上传到 Netlify**
   - 访问 https://app.netlify.com
   - 选择你的站点
   - 拖拽 ZIP 文件到部署区域
   - 或解压 ZIP，拖拽文件夹

4. **等待部署完成**

#### 优点：
- ✅ 简单直接
- ✅ 不需要 CLI
- ✅ 不需要 Git

#### 缺点：
- ❌ 需要手动操作
- ❌ 没有版本控制

---

## 📋 部署文件清单

需要部署的文件：

### 必需文件：
- ✅ `index.html` - 主页
- ✅ `landing.html` - Alpha 着陆页
- ✅ `dashboard.html` - Alpha 仪表板
- ✅ `signals_landing.html` - Signals 着陆页
- ✅ `signals_dashboard.html` - Signals 仪表板
- ✅ `terminal_landing.html` - Terminal 着陆页
- ✅ `terminal_dashboard.html` - Terminal 仪表板
- ✅ `privacy.html` - 隐私政策
- ✅ `terms.html` - 服务条款
- ✅ `netlify.toml` - Netlify 配置

### 不需要部署的文件：
- ❌ `main.py` - Python 后端（本地运行）
- ❌ `export_json.py` - Python 脚本（本地运行）
- ❌ `*.exe` - 可执行文件（本地运行）
- ❌ `*.bin` - 二进制文件（本地运行）
- ❌ `*.csv` - 数据文件（本地运行）
- ❌ `config.yml` - Cloudflared 配置（本地运行）
- ❌ `*.ps1` - PowerShell 脚本（本地运行）
- ❌ `*.bat` - 批处理脚本（本地运行）
- ❌ `*.py` - Python 脚本（本地运行）
- ❌ `static/` - 本地生成的数据（不部署）

---

## 🔧 自动化部署脚本说明

### `自动部署到Netlify.bat`

**功能：**
- 检查 Netlify CLI 是否安装
- 检查登录状态
- 自动部署到生产环境

**使用：**
```cmd
双击运行即可
```

**首次使用：**
- 会自动打开浏览器登录
- 授权后继续部署

---

### `打包部署文件.bat`

**功能：**
- 创建部署包目录
- 复制所有需要部署的文件
- 生成 ZIP 压缩包
- 自动打开文件位置

**使用：**
```cmd
双击运行
然后手动上传 ZIP 到 Netlify
```

---

## 📝 部署检查清单

部署前检查：

- [ ] 所有 HTML 文件已更新
- [ ] `netlify.toml` 配置正确
- [ ] 测试本地文件是否正常
- [ ] 检查链接是否正确
- [ ] 验证 API 地址（api.propkitai.tech）

部署后检查：

- [ ] 访问 https://propkitai.tech 正常
- [ ] 所有页面可以访问
- [ ] 链接跳转正常
- [ ] Dashboard 可以加载数据

---

## 🎯 推荐工作流程

### 开发阶段：
1. 修改代码
2. 本地测试
3. 运行验证脚本

### 部署阶段：
1. **方式一（推荐）**：运行 `自动部署到Netlify.bat`
2. **方式二（最佳）**：`git push`（如果设置了 Git 自动部署）
3. **方式三（备用）**：运行 `打包部署文件.bat`，手动上传

---

## ⚠️ 注意事项

1. **不要部署敏感文件**
   - 不要上传包含 API Key 的文件
   - 不要上传本地配置文件

2. **检查 netlify.toml**
   - 确保配置正确
   - 检查重定向规则

3. **测试部署**
   - 部署后立即测试
   - 检查所有功能

4. **保留备份**
   - 部署前备份重要文件
   - 使用 Git 进行版本控制

---

## 🚀 快速开始

### 最快方式（推荐）：

```cmd
双击: 自动部署到Netlify.bat
```

### 如果需要手动控制：

```cmd
双击: 打包部署文件.bat
然后拖拽 ZIP 到 Netlify
```

### 长期使用（最佳）：

设置 Git 自动部署，每次 `git push` 自动部署。

---

**现在可以选择最适合你的部署方式了！** 🎉
