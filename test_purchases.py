import requests
import random
import time
from datetime import datetime

# 你的本地后端地址
API_URL = "http://localhost:8000/api/webhook"

# 模拟的购买来源
SOURCES = ["Landing_Page_Alpha", "Checkout_Stripe", "Email_Campaign_V2", "Direct_Traffic"]

print("🚀 开始模拟购买意向流量...")

for i in range(1, 21):  # 模拟 20 个订单
    email = f"lead_investor_{random.randint(1000, 9999)}@hedgefund.com"
    source = random.choice(SOURCES)
    
    payload = {
        "email": email,
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # 发送 POST 请求给你的 main.py
        response = requests.post(API_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ [第 {i} 单] 成功捕获意向: {email} (来源: {source})")
        else:
            print(f"❌ [第 {i} 单] 失败: {response.text}")
            
    except Exception as e:
        print(f"⚠️ 连接错误: {e}")
    
    # 随机延迟，看起来像真实流量
    time.sleep(random.uniform(0.1, 0.5))

print("\n🎉 模拟完成！请刷新 purchase_stats.html 查看统计结果。")