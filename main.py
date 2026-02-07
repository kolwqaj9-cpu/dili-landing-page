import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
from api.create_purchase import create_purchase_endpoint

# ==================== 根目录路由 =====================

@app.get("/")
async def read_root():
    """强制定位到 Vercel 运行环境的根目录"""
    import os
    # 强制定位到 Vercel 运行环境的根目录
    root_dir = os.getcwd() 
    
    # 终极尝试列表：绝对路径
    potential_paths = [
        os.path.join(root_dir, "public", "index.html"),
        os.path.join(root_dir, "index.html"),
        "/var/task/public/index.html", # Vercel 的物理死路径
        "/var/task/index.html"
    ]
    
    for path in potential_paths:
        if os.path.exists(path):
            return FileResponse(path)
            
    return {"error": "Absolute failure", "current_work_dir": root_dir, "tried": potential_paths}

# ==================== API 路由 =====================

@app.post("/api/create_purchase")
async def create_purchase(request: Request):
    """创建购买记录接口 - 调用 api/create_purchase.py 中的函数"""
    return await create_purchase_endpoint(request, supabase)

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
