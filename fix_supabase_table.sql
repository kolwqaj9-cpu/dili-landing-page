-- Supabase reports 表修复 SQL
-- 在 Supabase Dashboard 的 SQL Editor 中执行

-- 方案1: 如果表已存在但没有 created_at 字段，添加字段
ALTER TABLE reports 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 方案2: 如果表完全不存在，创建完整表（通常不需要，因为表已存在）
-- CREATE TABLE IF NOT EXISTS reports (
--   id BIGSERIAL PRIMARY KEY,
--   user_email TEXT NOT NULL,
--   data_payload JSONB,
--   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- 为 created_at 字段创建索引（可选，提高查询性能）
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_user_email ON reports(user_email);

-- 验证表结构
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'reports'
ORDER BY ordinal_position;
