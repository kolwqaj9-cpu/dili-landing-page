-- 在 Supabase Dashboard 的 SQL Editor 中执行此脚本
-- 创建 purchases 表用于购买统计

CREATE TABLE IF NOT EXISTS purchases (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    source TEXT,
    amount DECIMAL(10, 2) DEFAULT 99.00,
    status TEXT DEFAULT 'intent_captured',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_purchases_user_email ON purchases(user_email);
CREATE INDEX IF NOT EXISTS idx_purchases_timestamp ON purchases(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_purchases_status ON purchases(status);

-- 启用 Row Level Security (RLS) - 可选
-- ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;

-- 验证表结构
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'purchases'
ORDER BY ordinal_position;
