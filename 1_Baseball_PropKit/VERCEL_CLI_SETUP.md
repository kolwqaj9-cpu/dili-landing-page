# Vercel CLI 安装和部署指南

## 前置要求：安装 Node.js

系统当前未安装 Node.js/npm，需要先安装才能使用 Vercel CLI。

### 安装步骤：

1. **下载 Node.js**
   - 访问：https://nodejs.org/
   - 下载 LTS 版本（推荐）
   - 运行安装程序，按默认选项安装

2. **验证安装**
   ```powershell
   node --version
   npm --version
   ```

3. **安装 Vercel CLI**
   ```powershell
   npm install -g vercel
   ```

4. **登录 Vercel**
   ```powershell
   vercel login
   ```
   - 会打开浏览器，完成登录

5. **关联项目**
   ```powershell
   vercel link
   ```
   - 选择项目：`baseprops-dgoa`
   - 或手动输入项目 ID

6. **生产部署**
   ```powershell
   vercel --prod
   ```

## 替代方案：通过 GitHub 自动部署

如果不想安装 Node.js，可以通过 GitHub 自动部署：
- 代码已推送到 GitHub
- Vercel 会自动检测并部署
- 访问 Vercel 仪表板查看部署状态

## 当前状态

- ✅ 代码已推送到 GitHub
- ✅ `vercel.json` 已配置
- ✅ HTML 文件已移动到 `public/` 文件夹
- ⏳ 等待 Vercel 自动部署或手动 CLI 部署
