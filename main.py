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

# ==================== 静态文件路由 ====================

@app.get("/")
async def root():
    """根路径返回 index.html"""
    return FileResponse("index.html")

@app.get("/checkout.html")
async def read_checkout():
    """显式处理 checkout.html 路由"""
    file_path = "checkout.html"  # 如果文件在根目录
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found locally"}

@app.get("/{filename}")
async def serve_html(filename: str):
    """为其他 HTML 文件提供路由"""
    if filename.endswith('.html'):
        if os.path.exists(filename):
            return FileResponse(filename)
    # 如果不是 HTML 文件或文件不存在，返回 404
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="File not found")

# 挂载 static 目录（用于 CSS、JS 等静态资源）
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
