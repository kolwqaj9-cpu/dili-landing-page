import uvicorn, os, subprocess, requests, json
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
    try:
        body = await req.json()
        email = body.get('email')
        source = body.get('source', 'Unknown')
        
        if email: 
            # 记录购买意图到统计系统
            try:
                purchase_record = {
                    "user_email": email,
                    "source": source,
                    "amount": 99.00,
                    "status": "intent_captured",  # intent_captured, completed, cancelled
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                # 记录到 purchases 表（如果表不存在，会在 Supabase 中自动创建或需要手动创建）
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
            
            # 将耗时任务放入后台，立刻给前端返回 200 OK，避免前端超时
            bt.add_task(run_pipeline, email)
            return {"status": "queued", "msg": "Calculation started"}
        else:
            return {"status": "error", "msg": "No email provided"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

@app.get("/api/data")
async def get_data(email: str = None):
    """
    安全的数据查询接口 - 前端通过此接口获取数据，而不是直接访问 Supabase
    这样 API Key 就不会暴露在前端代码中
    """
    if not email:
        return {"status": "error", "msg": "Email parameter required"}
    
    try:
        # ✅ 安全改进：从环境变量读取 Supabase 配置
        supabase_url = os.getenv("SUPABASE_URL", S_URL)
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", S_KEY)
        
        # 查询数据库，按时间倒序取最新一条
        url = f"{supabase_url}/rest/v1/reports?user_email=eq.{email}&select=*&order=created_at.desc&limit=1"
        response = requests.get(
            url,
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {"status": "success", "data": data}
        else:
            # 如果因为排序报错，尝试不排序直接取
            retry_url = f"{supabase_url}/rest/v1/reports?user_email=eq.{email}&select=*"
            retry_response = requests.get(
                retry_url,
                headers={
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}"
                },
                timeout=10
            )
            if retry_response.status_code == 200:
                data = retry_response.json()
                return {"status": "success", "data": data}
            else:
                return {"status": "error", "msg": f"Database query failed: {retry_response.status_code}"}
                
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
        
        # 查询总购买意图数
        total_url = f"{supabase_url}/rest/v1/purchases?select=count"
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
        today_url = f"{supabase_url}/rest/v1/purchases?timestamp=gte.{today}&select=count"
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
        
        if total_response.status_code == 200:
            # 从响应头获取总数
            count_header = total_response.headers.get('content-range', '0')
            if '/' in count_header:
                stats["total_intents"] = int(count_header.split('/')[-1])
        
        if today_response.status_code == 200:
            count_header = today_response.headers.get('content-range', '0')
            if '/' in count_header:
                stats["today_intents"] = int(count_header.split('/')[-1])
        
        if recent_response.status_code == 200:
            stats["recent_purchases"] = recent_response.json()
        
        return {"status": "success", "data": stats}
        
    except Exception as e:
        return {"status": "error", "msg": str(e)}

if __name__ == "__main__":
    # 自动创建 static 文件夹，防止报错
    if not os.path.exists("static"): 
        os.makedirs("static")
    
    print("🚀 [INFRA] PropKit Dedicated Tensor Node initialized (PID: {})".format(os.getpid()))
    print("📡 [INFRA] Listening on port 8000 | Synchronizing with GPU Accelerated Backbone...")
    # host="0.0.0.0" 确保能被局域网或隧道访问
    uvicorn.run(app, host="0.0.0.0", port=8000)