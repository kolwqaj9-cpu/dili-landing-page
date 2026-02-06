"""
创建购买记录接口
使用 supabase-py 库向 purchases 表插入记录
"""
from fastapi import Request
from datetime import datetime, timezone
from supabase import Client

async def create_purchase_endpoint(request: Request, supabase: Client):
    """
    创建购买记录接口
    接收 POST 请求中的 email 和 amount，向 purchases 表插入一条 status='paid' 的记录
    """
    try:
        body = await request.json()
        email = body.get('email', 'unknown')
        amount = body.get('amount', 99.00)
        status = body.get('status', 'paid')  # 默认状态为 paid
        
        # 使用 supabase-py 库插入到 purchases 表
        response = supabase.table("purchases").insert({
            "user_email": email,
            "amount": amount,
            "status": status,
            "source": "Web_Direct",
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        print(f"✅ [Purchase] 新订单已创建: {email}, 金额: ${amount}, 状态: {status}")
        
        return {
            "status": "success",
            "message": "Purchase recorded successfully",
            "data": response.data[0] if response.data else None
        }
    except Exception as e:
        print(f"❌ [Purchase] 创建订单失败: {str(e)}")
        return {"status": "error", "message": str(e)}
