import uvicorn, os, random, hashlib, requests
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 数据库配置 (会从 Render 环境变量读取)
S_URL = os.getenv("SUPABASE_URL")
S_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# --- 核心功能 1: 心理安慰剂 (生成看起来很厉害的假数据) ---
def get_comfort_data(email: str):
    # 生成 5 条看着很专业的信号
    signals = []
    for i in range(5):
        match_hash = hashlib.md5(f"{email}_{i}_{datetime.now()}".encode()).hexdigest()[:8].upper()
        signals.append({
            "match_id": f"PREMIUM_SIGNAL_{match_hash}",
            "confidence_score": round(random.uniform(92.0, 99.0), 1), # 信心满满
            "ev_value": f"+{round(random.uniform(5.0, 18.0), 2)}%",   # 看着就赚钱
            "alpha_tag": random.choice(["INSTITUTIONAL FLOW", "SHARP MONEY", "VEGAS ANOMALY"]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return {
        "total_analyzed": random.randint(150000, 200000),
        "target_count": random.randint(15, 30), # 只有极少数精华
        "data": signals, # 前端图表会用到
        "signals": signals,
        "compute_metadata": {
            "node_id": "CLOUD-H100-VIRTUAL",
            "status": "OPTIMIZED"
        }
    }

# --- 接口 1: 购买记录 (收银台) ---
@app.post("/api/webhook")
async def hook(req: Request):
    try:
        body = await req.json()
        email = body.get('email')
        source = body.get('source', 'Web')
        
        # 写入 Supabase 记账
        if S_URL and S_KEY and email:
            try:
                requests.post(
                    f"{S_URL}/rest/v1/purchases",
                    json={
                        "user_email": email, 
                        "source": source, 
                        "amount": 99.00,
                        "status": "intent_captured"
                    },
                    headers={
                        "apikey": S_KEY, "Authorization": f"Bearer {S_KEY}",
                        "Content-Type": "application/json", "Prefer": "return=minimal"
                    },
                    timeout=5
                )
                print(f"💰 [新订单] {email} 意向已记录")
            except Exception as db_err:
                print(f"⚠️ 记账失败 (不影响用户): {db_err}")

        # 直接返回成功，让用户赶紧去体验"安慰剂"
        return {"status": "queued", "msg": "Premium access granted"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

# --- 接口 2: 获取安慰数据 (Dashboard) ---
@app.get("/api/data")
async def get_data(email: str = "guest"):
    # 纯模拟，0 延迟，秒开
    fake_payload = get_comfort_data(email)
    return {
        "status": "success", 
        "data": [{
            "user_email": email,
            "data_payload": fake_payload,
            "created_at": datetime.now(timezone.utc).isoformat()
        }]
    }

# --- 接口 3: 老板查账 (你的统计页面) ---
@app.get("/api/stats/purchases")
async def get_stats():
    if not S_URL or not S_KEY:
        return {"status": "error", "msg": "Database config missing"}
    
    try:
        # 查总数
        r = requests.get(
            f"{S_URL}/rest/v1/purchases?select=count",
            headers={"apikey": S_KEY, "Authorization": f"Bearer {S_KEY}", "Prefer": "count=exact"}
        )
        total = int(r.headers.get('content-range', '0/0').split('/')[1])
        
        # 查最近 10 单
        r_list = requests.get(
            f"{S_URL}/rest/v1/purchases?select=*&order=timestamp.desc&limit=10",
            headers={"apikey": S_KEY, "Authorization": f"Bearer {S_KEY}"}
        )
        return {"status": "success", "data": {"total_intents": total, "recent_purchases": r_list.json()}}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
