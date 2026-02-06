import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从 Vercel 环境变量读取密钥
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

from fastapi import Request
from datetime import datetime, timezone

@app.post("/api/purchases/create")
async def create_purchase(request: Request):
    """创建购买记录接口"""
    try:
        body = await request.json()
        email = body.get('email', 'unknown')
        amount = body.get('amount', 99.00)
        status = body.get('status', 'paid')
        
        # 插入到 Supabase 数据库
        response = supabase.table("purchases").insert({
            "user_email": email,
            "amount": amount,
            "status": status,
            "source": "Web_Direct",
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        return {
            "status": "success",
            "message": "Purchase recorded",
            "data": response.data[0] if response.data else None
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/stats/purchases")
async def get_stats():
    try:
        # 实时从数据库统计 status 为 'paid' 的订单
        response = supabase.table("purchases").select("*").eq("status", "paid").execute()
        data = response.data
        
        return {
            "status": "success",
            "data": {
                "total_intents": len(data),
                "total_revenue": sum(item.get("amount", 0) for item in data),
                "recent_purchases": data[:10]  # 返回最近10条记录
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "PropKit Backend is Live"}
