# 核心部署指南

## 最小化核心包

已创建最小化核心部署包，只包含核心功能：

### 包含文件
- `index.html` - 主页（带版本标识）
- `landing.html` - 核心功能页面（带版本标识）
- `dashboard.html` - 结果显示页面
- `netlify.toml` - Netlify 配置（API 代理）

### 文件信息
- **文件名**: `netlify_core_20260203_214755.zip`
- **大小**: 9.80 KB
- **位置**: 项目根目录

## 部署步骤

1. **访问 Netlify**
   - 打开: https://app.netlify.com
   - 选择站点: propkitai.tech

2. **上传 ZIP 文件**
   - 拖拽 `netlify_core_*.zip` 到部署区域
   - 等待部署完成（通常 10-30 秒）

3. **发布部署**
   - 点击 "Publish deploy" 按钮
   - 等待 1-2 分钟让 CDN 更新

## 验证部署

### 方法 1: 自动验证
运行脚本：
```
.\快速验证部署.bat
```

### 方法 2: 手动验证
1. 访问: https://propkitai.tech/landing.html
2. 检查页面顶部是否显示：
   - **"VERSION 3.0 - DEPLOYED"** (右上角)
   - **"⚠️ DEPLOYMENT VERSION 3.0 - If you see this, deployment was successful!"** (页面中央)

3. 如果看到版本标识 → **部署成功** ✅
4. 如果看不到版本标识 → **部署失败或未发布** ❌

## 连接功能

### 前提条件
连接功能需要后端服务运行：

1. **启动服务**
   ```
   .\start_services.ps1
   ```
   或
   ```
   .\一键启动.bat
   ```

2. **等待服务启动**（10-15 秒）

3. **验证服务**
   - 应该看到两个窗口（Cloudflared 和 Python 后端）
   - 或运行诊断脚本确认

### 测试连接
1. 访问: https://propkitai.tech/landing.html
2. 点击 "Request Access"
3. 输入邮箱
4. 点击 "ACTIVATE FREE TRIAL"
5. ✅ 如果成功 → 后端服务正常
6. ❌ 如果失败 → 检查后端服务是否运行

## 问题排查

### 部署问题
- **看不到版本标识**
  - 检查是否点击了 "Publish deploy"
  - 等待 2-5 分钟让 CDN 更新
  - 清除浏览器缓存（Ctrl+F5）
  - 使用无痕窗口测试

### 连接问题
- **连接错误**
  - 确认后端服务已启动
  - 运行诊断脚本: `.\comprehensive_diagnosis.py`
  - 检查 Cloudflared 和 Python 后端是否运行

## 下一步

核心功能部署成功后，可以：
1. 添加其他页面（signals_landing, terminal_landing 等）
2. 添加隐私政策和条款页面
3. 优化 UI 和用户体验
