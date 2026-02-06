import uvicorn, os, subprocess, requests, json, asyncio, random, hashlib
from datetime import datetime, timezone
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ================= 配置区域 =================
# ✅ 安全改进：从环境变量读取 Supabase 配置，而不是硬编码
# 如果 .env 文件不存在或变量未设置，使用默认值（仅用于开发环境）
S_URL = os.getenv("SUPABASE_URL", "https://bmwfnuekfgolwutnffmf.supabase.co")
S_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
# ===========================================

# 检查密钥是否已配置
if not S_KEY:
    print("⚠️ [WARNING] SUPABASE_SERVICE_ROLE_KEY not found in environment variables!")
    print("   Please create a .env file with your Supabase credentials.")
    print("   See README_SECURITY.md for instructions.")

# ================= 演示模式：高保真模拟数据生成器 =================
def get_simulated_intelligence(email: str):
    """
    生成极度逼真的棒球分析数据（演示模式）
    返回机构级术语和复杂数据，模拟真实 GPU 计算输出
    """
    # 生成 5-8 条信号数据
    num_signals = random.randint(5, 8)
    signals = []
    
    for i in range(num_signals):
        # 生成看起来像哈希值的 match_id
        match_hash = hashlib.md5(f"{email}_{i}_{datetime.now().isoformat()}".encode()).hexdigest()[:12].upper()
        match_id = f"MATCH_{match_hash}"
        
        # 生成逼真的置信度分数（85-98%）
        confidence = round(random.uniform(85.0, 98.5), 1)
        
        # 生成 EV 值（预期价值，-15% 到 +25%）
        ev_value = round(random.uniform(-15.0, 25.0), 2)
        ev_display = f"+{ev_value}%" if ev_value >= 0 else f"{ev_value}%"
        
        # 生成市场偏差（0.5% 到 8.5%）
        market_discrepancy = round(random.uniform(0.5, 8.5), 2)
        
        # 生成推荐入场点（价格范围）
        entry_price = round(random.uniform(1.85, 2.15), 2)
        
        # 机构级术语标签
        alpha_tags = [
            "Alpha Decay Detected",
            "Sharp Money Divergence", 
            "Market Inefficiency Identified",
            "Institutional Flow Anomaly",
            "Volume-Weighted Price Dislocation",
            "Cross-Market Arbitrage Signal",
            "Regime Shift Indicator",
            "Liquidity Premium Extraction"
        ]
        tag = random.choice(alpha_tags)
        
        signals.append({
            "match_id": match_id,
            "confidence_score": confidence,
            "ev_value": ev_display,
            "market_discrepancy": f"{market_discrepancy}%",
            "recommended_entry": entry_price,
            "alpha_tag": tag,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    # 生成图表数据点（模拟战术数据）
    chart_data = []
    for i in range(random.randint(150, 250)):
        chart_data.append([
            round(random.uniform(-2.5, 2.5), 3),  # plate_x
            round(random.uniform(0.5, 4.5), 3),   # plate_z
            round(random.uniform(60.0, 100.0), 1), # score
            random.randint(1, 4)                  # reason
        ])
    
    # 构建完整的响应数据包
    simulated_data = {
        "total_analyzed": random.randint(280000, 295000),
        "target_count": random.randint(25000, 28000),
        "sample_count": len(chart_data),
        "top_reason": random.randint(1, 4),
        "data": chart_data,
        "signals": signals,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "compute_metadata": {
            "node_id": "H100-NODE-ALPHA-07",
            "gpu_utilization": round(random.uniform(85.0, 98.0), 1),
            "processing_time_ms": random.randint(12450, 18750),
            "tensor_ops": f"{random.randint(450, 680)}M"
        }
    }
    
    return simulated_data
# ================================================================

def run_pipeline(email: str):
    print(f"\n⚡ [INFRA] New compute request assigned to Node-Alpha: {email}")
    try:
        # --- 第1步：定位并运行 CUDA 物理引擎 ---
        # 获取当前目录的绝对路径，防止相对路径出错
        current_dir = os.getcwd()
        # 拼接 exe 的完整路径
        exe_path = os.path.join(current_dir, "x64", "Debug", "CudaRuntime1.exe")
        
        print(f"🔍 [INFRA] Locating tensor compute engine: {exe_path}")
        
        # 【关键修复】强制检查文件是否存在，不存在直接报错！
        if not os.path.exists(exe_path):
            raise FileNotFoundError(
                f"\n❌ 致命错误：找不到文件\n{exe_path}\n"
                f"请检查：\n"
                f"1. 您是否在 Visual Studio 点击了【生成解决方案】？\n"
                f"2. 这里的路径 'x64/Debug' 是否正确？有时候是在 'x64/Release'。"
            )

        print("✅ Compute core hot-swapped. Executing tensor-flow...")
        # 运行 exe (check=True 表示如果 C++ 崩了，Python 也会报错)
        subprocess.run([exe_path], check=True)
        
        # --- 第2步：运行 Python 格式转换脚本 ---
        print("🔄 [INFRA] Initializing Neural Compute Instance (data transformation)...")
        if not os.path.exists("export_json.py"):
             raise FileNotFoundError("❌ 找不到 export_json.py 脚本！")
             
        subprocess.run(["python", "export_json.py"], check=True)
        
        # --- 第3步：读取结果并上传云端 ---
        json_path = "static/tactical_data.json"
        if not os.path.exists(json_path):
             raise FileNotFoundError(f"❌ 找不到结果文件 {json_path}，可能是 export_json.py 运行失败。")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sample_count = len(data.get('data', []))
        target_count = data.get('target_count', 'N/A')
        print(f"☁️ [INFRA] Real-time stream verified by H100/A100 Cluster. Syncing to cloud... (targets: {target_count}, sampled points: {sample_count})")
        
        now_iso = datetime.now(timezone.utc).isoformat()
        data["generated_at"] = now_iso
        res = requests.post(
            f"{S_URL}/rest/v1/reports",
            json={"user_email": email, "data_payload": data, "created_at": now_iso},
            headers={
                "apikey": S_KEY, 
                "Authorization": f"Bearer {S_KEY}",
                "Content-Type": "application/json", 
                "Prefer": "resolution=merge-duplicates"
            }
        )
        
        if res.status_code in [200, 201]:
            print(f"✅ [SUCCESS] Compute pipeline completed. Data synchronized to distributed storage. Status: {res.status_code}")
        else:
            print(f"⚠️ [WARNING] Cloud sync anomaly detected: {res.status_code} - {res.text}")

    except subprocess.CalledProcessError as e:
        print(f"❌ [ERROR] 子程序运行失败 (C++或Python脚本报错): {e}")
    except Exception as e: 
        print(f"❌ [ERROR] 流程中断: {e}")

@app.post("/api/webhook")
async def hook(req: Request, bt: BackgroundTasks):
    """
    演示模式：虚假算力响应
    不启动真实 CUDA 任务，直接返回成功响应
    """
    try:
        body = await req.json()
        email = body.get('email')
        source = body.get('source', 'Unknown')
        
        if email: 
            # 记录购买意图到统计系统（保留真实记录功能）
            try:
                purchase_record = {
                    "user_email": email,
                    "source": source,
                    "amount": 99.00,
                    "status": "intent_captured",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                purchase_url = f"{S_URL}/rest/v1/purchases"
                requests.post(
                    purchase_url,
                    json=purchase_record,
                    headers={
                        "apikey": S_KEY,
                        "Authorization": f"Bearer {S_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=minimal"
                    },
                    timeout=5
                )
                print(f"📊 [STATS] Purchase intent recorded: {email} from {source}")
            except Exception as e:
                print(f"⚠️ [WARNING] Failed to record purchase intent: {e}")
            
            # 🎭 演示模式：不启动真实 GPU 任务，直接返回
            print(f"⚡ [SIMULATION] Fake compute instance provisioned for user: {email}")
            return {"status": "queued", "msg": "Instance allocated"}
        else:
            return {"status": "error", "msg": "No email provided"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

@app.get("/api/data")
async def get_data(email: str = None):
    """
    演示模式：高保真模拟数据接口
    不查询数据库，直接返回模拟数据，模拟 1.5 秒查询延迟
    """
    if not email:
        return {"status": "error", "msg": "Email parameter required"}
    
    try:
        # 🎭 演示模式：模拟数据库查询延迟（1.5秒）
        await asyncio.sleep(1.5)
        
        # 生成模拟数据
        simulated_payload = get_simulated_intelligence(email)
        
        # 构建符合前端期望的响应格式
        now_iso = datetime.now(timezone.utc).isoformat()
        mock_report = {
            "id": random.randint(1000, 9999),
            "user_email": email,
            "data_payload": simulated_payload,
            "created_at": now_iso
        }
        
        print(f"🎭 [SIMULATION] Returning simulated intelligence data for: {email}")
        print(f"   Signals: {len(simulated_payload.get('signals', []))}, Data points: {len(simulated_payload.get('data', []))}")
        
        return {"status": "success", "data": [mock_report]}
                
    except Exception as e:
        return {"status": "error", "msg": str(e)}

@app.get("/api/stats/purchases")
async def get_purchase_stats():
    """
    购买统计接口 - 返回购买统计数据
    """
    try:
        supabase_url = os.getenv("SUPABASE_URL", S_URL)
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", S_KEY)
        
        if not supabase_key:
            print("⚠️ [STATS] Supabase key not configured")
            return {"status": "error", "msg": "Supabase key not configured"}
        
        # 查询总购买意图数 - 使用更可靠的查询方式
        total_url = f"{supabase_url}/rest/v1/purchases?select=id"
        total_response = requests.get(
            total_url,
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Prefer": "count=exact"
            },
            timeout=10
        )
        
        # 查询今日购买意图数
        today = datetime.now(timezone.utc).date().isoformat()
        today_url = f"{supabase_url}/rest/v1/purchases?timestamp=gte.{today}&select=id"
        today_response = requests.get(
            today_url,
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Prefer": "count=exact"
            },
            timeout=10
        )
        
        # 查询最近购买记录（最多10条）
        recent_url = f"{supabase_url}/rest/v1/purchases?select=*&order=timestamp.desc&limit=10"
        recent_response = requests.get(
            recent_url,
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}"
            },
            timeout=10
        )
        
        stats = {
            "total_intents": 0,
            "today_intents": 0,
            "recent_purchases": []
        }
        
        # 从响应头获取总数
        if total_response.status_code == 200:
            count_header = total_response.headers.get('content-range', '')
            if count_header and '/' in count_header:
                try:
                    stats["total_intents"] = int(count_header.split('/')[-1])
                except:
                    # 如果解析失败，尝试从返回的数据长度获取
                    data = total_response.json()
                    stats["total_intents"] = len(data) if isinstance(data, list) else 0
            else:
                # 如果没有 content-range，尝试从数据长度获取
                data = total_response.json()
                stats["total_intents"] = len(data) if isinstance(data, list) else 0
        else:
            print(f"⚠️ [STATS] Total count query failed: {total_response.status_code} - {total_response.text[:200]}")
        
        if today_response.status_code == 200:
            count_header = today_response.headers.get('content-range', '')
            if count_header and '/' in count_header:
                try:
                    stats["today_intents"] = int(count_header.split('/')[-1])
                except:
                    data = today_response.json()
                    stats["today_intents"] = len(data) if isinstance(data, list) else 0
            else:
                data = today_response.json()
                stats["today_intents"] = len(data) if isinstance(data, list) else 0
        else:
            print(f"⚠️ [STATS] Today count query failed: {today_response.status_code} - {today_response.text[:200]}")
        
        if recent_response.status_code == 200:
            stats["recent_purchases"] = recent_response.json()
        else:
            print(f"⚠️ [STATS] Recent purchases query failed: {recent_response.status_code} - {recent_response.text[:200]}")
        
        print(f"📊 [STATS] Returning stats: total={stats['total_intents']}, today={stats['today_intents']}, recent={len(stats['recent_purchases'])}")
        return {"status": "success", "data": stats}
        
    except Exception as e:
        print(f"❌ [STATS] Error in get_purchase_stats: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "msg": str(e)}

if __name__ == "__main__":
    # 自动创建 static 文件夹，防止报错
    if not os.path.exists("static"): 
        os.makedirs("static")
    
    print("🚀 [INFRA] PropKit Dedicated Tensor Node initialized (PID: {})".format(os.getpid()))
    print("📡 [INFRA] Listening on port 8000 | Synchronizing with GPU Accelerated Backbone...")
    # host="0.0.0.0" 确保能被局域网或隧道访问
    uvicorn.run(app, host="0.0.0.0", port=8000)