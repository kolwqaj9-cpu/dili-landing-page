"""
模拟购买意向测试脚本
用于验证购买统计功能是否正常工作
"""
import requests
import json
import time
from datetime import datetime

# API 配置
API_BASE = "http://localhost:8000"
WEBHOOK_URL = f"{API_BASE}/api/webhook"
STATS_URL = f"{API_BASE}/api/stats/purchases"

# 模拟用户邮箱列表
test_users = [
    "alpha.trader@institutional.com",
    "quant.analyst@hedgefund.io",
    "prop.desk@marketmaker.com",
    "research.team@propfirm.net",
    "signal.subscriber@trading.com"
]

def simulate_purchase_intent(email: str, source: str = "Signals_Checkout_Page"):
    """模拟一个购买意向请求"""
    try:
        payload = {
            "email": email,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {email[:30]:<30} | Status: {result.get('status')} | {result.get('msg')}")
            return True
        else:
            print(f"❌ {email[:30]:<30} | Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ {email[:30]:<30} | Exception: {e}")
        return False

def get_purchase_stats():
    """获取购买统计数据"""
    try:
        response = requests.get(STATS_URL, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return result.get('data', {})
        print(f"⚠️ 获取统计失败: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"❌ 获取统计异常: {e}")
        return None

def main():
    print("=" * 70)
    print("🎭 购买意向模拟测试")
    print("=" * 70)
    print()
    
    # 先查看初始统计
    print("📊 初始统计数据：")
    initial_stats = get_purchase_stats()
    if initial_stats:
        print(f"   总购买意图数: {initial_stats.get('total_intents', 0)}")
        print(f"   今日购买意图数: {initial_stats.get('today_intents', 0)}")
        print(f"   预估收入: ${(initial_stats.get('total_intents', 0) * 99):,}")
    print()
    
    # 模拟购买请求
    print("🚀 开始模拟购买意向...")
    print("-" * 70)
    
    success_count = 0
    for i, email in enumerate(test_users, 1):
        print(f"[{i}/{len(test_users)}] 模拟用户: {email}")
        if simulate_purchase_intent(email):
            success_count += 1
        time.sleep(0.5)  # 短暂延迟，避免请求过快
    
    print()
    print("-" * 70)
    print(f"✅ 成功模拟: {success_count}/{len(test_users)} 个购买意向")
    print()
    
    # 等待一下，让数据写入数据库
    print("⏳ 等待 2 秒，让数据同步到数据库...")
    time.sleep(2)
    print()
    
    # 再次查看统计
    print("📊 更新后的统计数据：")
    final_stats = get_purchase_stats()
    if final_stats:
        total = final_stats.get('total_intents', 0)
        today = final_stats.get('today_intents', 0)
        revenue = total * 99
        
        print(f"   总购买意图数: {total} (增加: {total - (initial_stats.get('total_intents', 0) if initial_stats else 0)})")
        print(f"   今日购买意图数: {today}")
        print(f"   预估收入: ${revenue:,}")
        print()
        
        # 显示最近购买记录
        recent = final_stats.get('recent_purchases', [])
        if recent:
            print("📋 最近购买记录（前 5 条）：")
            for i, purchase in enumerate(recent[:5], 1):
                timestamp = purchase.get('timestamp', purchase.get('created_at', 'N/A'))
                print(f"   {i}. {purchase.get('user_email', 'N/A')[:35]:<35} | "
                      f"${purchase.get('amount', 0):.2f} | "
                      f"{purchase.get('status', 'N/A')} | "
                      f"{timestamp[:19] if len(timestamp) > 19 else timestamp}")
        else:
            print("   (暂无最近购买记录)")
    
    print()
    print("=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
