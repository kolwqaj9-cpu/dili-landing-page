import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# ==================== API 路由（必须在静态文件之前定义）====================

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

# ==================== 静态文件路由（显式路由，不使用通配符）====================

@app.get("/")
async def root():
    """根路径返回 index.html"""
    return FileResponse("index.html")

@app.get("/checkout.html")
async def serve_checkout():
    """显式处理 checkout.html 路由"""
    return FileResponse("checkout.html")

@app.get("/purchase_stats.html")
async def serve_stats_page():
    """显式处理 purchase_stats.html 路由"""
    return FileResponse("purchase_stats.html")

@app.get("/signals_dashboard.html")
async def serve_signals_dashboard():
    """显式处理 signals_dashboard.html 路由"""
    return FileResponse("signals_dashboard.html")

@app.get("/landing.html")
async def serve_landing():
    """显式处理 landing.html 路由"""
    return FileResponse("landing.html")

@app.get("/terms.html")
async def serve_terms():
    """显式处理 terms.html 路由"""
    return FileResponse("terms.html")

@app.get("/privacy.html")
async def serve_privacy():
    """显式处理 privacy.html 路由"""
    return FileResponse("privacy.html")

@app.get("/index.html")
async def serve_index():
    """显式处理 index.html 路由"""
    return FileResponse("index.html")

# 挂载 static 目录（用于 CSS、JS 等静态资源）
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
