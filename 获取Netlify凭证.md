# 如何获取 Netlify API Token 和 Site ID

## 🔑 获取 API Token

### 步骤：

1. **访问 Netlify**
   - 打开：https://app.netlify.com
   - 登录你的账户

2. **进入用户设置**
   - 点击右上角头像
   - 选择 "User settings"

3. **创建 Access Token**
   - 点击左侧菜单 "Applications"
   - 点击 "New access token"
   - 输入名称（例如：Auto Deploy）
   - 点击 "Generate token"

4. **复制 Token**
   - ⚠️ **重要**：Token 只显示一次，立即复制保存
   - 格式类似：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🆔 获取 Site ID

### 步骤：

1. **访问你的站点**
   - 在 Netlify Dashboard 中选择你的站点（propkitai.tech）

2. **进入站点设置**
   - 点击 "Site settings"
   - 或点击站点名称旁边的设置图标

3. **查看 Site details**
   - 在左侧菜单选择 "General"
   - 找到 "Site details" 部分
   - 复制 "Site ID"
   - 格式类似：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## 📝 使用说明

### 首次使用：

1. **运行脚本**
   ```cmd
   双击: 运行自动上传.bat
   ```

2. **输入凭证**
   - 脚本会提示输入 API Token
   - 然后提示输入 Site ID
   - 粘贴你刚才获取的值

3. **自动保存**
   - 凭证会自动保存到 `.netlify_config.json`
   - 下次使用不需要再输入

### 后续使用：

直接运行脚本即可，无需输入凭证！

```cmd
双击: 运行自动上传.bat
```

---

## 🔒 安全提示

- ✅ `.netlify_config.json` 文件包含敏感信息
- ✅ 不要将此文件提交到 Git
- ✅ 不要分享此文件
- ✅ 如果泄露，立即在 Netlify 中撤销 Token

---

## 🚀 完整流程

1. **获取凭证**（只需一次）
   - API Token
   - Site ID

2. **运行脚本**
   ```cmd
   双击: 运行自动上传.bat
   ```

3. **首次输入凭证**
   - 粘贴 API Token
   - 粘贴 Site ID

4. **自动上传**
   - 脚本自动打包文件
   - 自动上传到 Netlify
   - 显示部署结果

5. **完成**
   - 访问 https://propkitai.tech 查看更新

---

## ❓ 常见问题

### Q: Token 在哪里使用？
A: 只在首次运行时输入，之后自动保存。

### Q: 可以修改凭证吗？
A: 删除 `.netlify_config.json` 文件，重新运行脚本。

### Q: 上传失败怎么办？
A: 检查：
- API Token 是否正确
- Site ID 是否正确
- 网络连接是否正常

---

**现在可以完全自动化部署了！** 🎉
