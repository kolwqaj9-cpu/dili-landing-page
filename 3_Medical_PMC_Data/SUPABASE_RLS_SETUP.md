# Supabase RLS (Row Level Security) 配置指南

## ⚠️ 重要：必须配置 RLS 才能使用 Anon Key

使用 Anon Key 在前端直接连接 Supabase 是安全的，但**必须正确配置 RLS (Row Level Security)**，否则：
- 无法插入数据（checkout.html 会失败）
- 无法读取数据（purchase_stats.html 会失败）

## 配置步骤

### 1. 登录 Supabase Dashboard
访问：https://supabase.com/dashboard
选择你的项目：`base2` (bmwfnuekfgolwutnffmf)

### 2. 打开 SQL Editor
在左侧菜单找到 "SQL Editor"，点击 "New query"

### 3. 执行以下 SQL 配置 RLS

```sql
-- 1. 启用 RLS 策略
ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;

-- 2. 允许任何人（anon）插入购买记录
CREATE POLICY "Allow anon insert" ON purchases
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- 3. 允许任何人（anon）读取所有购买记录（用于统计页面）
CREATE POLICY "Allow anon select" ON purchases
    FOR SELECT
    TO anon
    USING (true);
```

### 4. 验证配置
执行以下查询确认策略已创建：

```sql
SELECT * FROM pg_policies WHERE tablename = 'purchases';
```

应该看到两条策略：
- `Allow anon insert` (INSERT)
- `Allow anon select` (SELECT)

## ✅ 验证测试

### 测试插入（checkout.html）
1. 访问 `checkout.html?email=test@example.com`
2. 点击 "Confirm Payment $99"
3. 检查浏览器控制台（F12），应该没有错误
4. 应该成功跳转到 `signals_dashboard.html`

### 测试读取（purchase_stats.html）
1. 访问 `purchase_stats.html`
2. 应该能看到刚才插入的测试记录
3. 总数和列表都应该正常显示

## 🔒 安全说明

### 为什么 Anon Key 是安全的？
- **Anon Key** 是公开的，任何人都能看到
- 但通过 **RLS 策略**，我们限制了它能做什么：
  - ✅ 只能插入新记录（不能修改或删除）
  - ✅ 只能读取所有记录（用于统计，这是合理的）
  - ❌ 不能删除数据
  - ❌ 不能修改已有数据

### 如果使用 Service Role Key 会怎样？
- ⚠️ **Service Role Key 可以绕过所有 RLS 策略**
- ⚠️ 如果放在前端代码中，任何人都能：
  - 删除整个数据库
  - 修改任何数据
  - 读取敏感信息
- ❌ **永远不要在前端代码中使用 Service Role Key！**

## 🎯 当前配置总结

- ✅ 使用 Anon Key（安全）
- ✅ RLS 已配置（限制权限）
- ✅ 前端直接连接 Supabase（无需后端）
- ✅ 完全静态部署（GitHub Pages）

## 故障排查

### 问题：插入失败，提示 "new row violates row-level security policy"
**解决**：检查 RLS 策略是否正确创建，确保有 "Allow anon insert" 策略

### 问题：读取失败，提示 "permission denied"
**解决**：检查是否有 "Allow anon select" 策略

### 问题：策略已创建但仍然失败
**解决**：
1. 确认表名是 `purchases`（不是 `purchase` 或其他）
2. 确认策略的 `TO anon` 部分正确
3. 尝试刷新 Supabase Dashboard 页面
