"""
手动上传测试脚本
测试将本地生成的 JSON 文件上传到 Supabase
"""

import json
import requests
import os
import sys
from datetime import datetime

# Supabase 配置
S_URL = "https://vlrdiajxxnangawfcgvk.supabase.co"
S_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZscmRpYWp4eG5hbmdhd2ZjZ3ZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTkxNzYyNiwiZXhwIjoyMDg1NDkzNjI2fQ.WJGxW0o_NFa9lgu_tJ1otsxjxI8-3O6RPIkjLMFRYEg"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_upload(email=None):
    """测试上传 JSON 到 Supabase"""
    print_section("Supabase 上传测试")
    
    # 检查 JSON 文件
    json_path = "static/tactical_data.json"
    
    if not os.path.exists(json_path):
        print(f"  ❌ JSON 文件不存在: {json_path}")
        print(f"  请先运行本地计算测试生成 JSON 文件")
        return False
    
    print(f"  ✅ JSON 文件存在: {json_path}")
    
    # 读取 JSON 数据
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  数据内容:")
        print(f"    总分析数: {data.get('total_analyzed', 'N/A')}")
        print(f"    目标数: {data.get('target_count', 'N/A')}")
        print(f"    数据点: {len(data.get('data', []))}")
    except Exception as e:
        print(f"  ❌ 读取 JSON 失败: {e}")
        return False
    
    # 生成测试邮箱
    if not email:
        email = f"test_upload_{int(datetime.now().timestamp())}@test.com"
    
    print(f"\n  测试邮箱: {email}")
    print(f"  开始上传...")
    
    # 上传到 Supabase
    try:
        response = requests.post(
            f"{S_URL}/rest/v1/reports",
            json={"user_email": email, "data_payload": data},
            headers={
                "apikey": S_KEY,
                "Authorization": f"Bearer {S_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"  ✅ 上传成功！")
            print(f"  状态码: {response.status_code}")
            print(f"  记录 ID: {result[0].get('id', 'N/A') if isinstance(result, list) else result.get('id', 'N/A')}")
            print(f"  创建时间: {result[0].get('created_at', 'N/A') if isinstance(result, list) else result.get('created_at', 'N/A')}")
            
            return True, email
        else:
            print(f"  ❌ 上传失败")
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text[:500]}")
            return False, email
    except Exception as e:
        print(f"  ❌ 上传失败: {e}")
        import traceback
        traceback.print_exc()
        return False, email

def verify_upload(email):
    """验证上传的数据"""
    print_section("验证上传的数据")
    
    try:
        response = requests.get(
            f"{S_URL}/rest/v1/reports?user_email=eq.{email}&order=id.desc&limit=1",
            headers={
                "apikey": S_KEY,
                "Authorization": f"Bearer {S_KEY}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                record = data[0]
                print(f"  ✅ 数据验证成功")
                print(f"  记录 ID: {record.get('id', 'N/A')}")
                print(f"  邮箱: {record.get('user_email', 'N/A')}")
                
                if record.get('data_payload'):
                    payload = record['data_payload']
                    print(f"  总分析数: {payload.get('total_analyzed', 'N/A')}")
                    print(f"  目标数: {payload.get('target_count', 'N/A')}")
                    print(f"  数据点: {len(payload.get('data', []))}")
                
                print(f"\n  Dashboard 链接:")
                print(f"  https://propkitai.tech/dashboard.html?email={email}")
                
                return True
            else:
                print(f"  ⚠️  未找到数据")
                return False
        else:
            print(f"  ❌ 查询失败 (状态码: {response.status_code})")
            print(f"  响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  Supabase 手动上传测试工具")
    print("=" * 60)
    
    # 检查连接
    print_section("检查 Supabase 连接")
    try:
        response = requests.get(
            f"{S_URL}/rest/v1/",
            headers={
                "apikey": S_KEY,
                "Authorization": f"Bearer {S_KEY}"
            },
            timeout=5
        )
        if response.status_code == 200:
            print("  ✅ Supabase 连接正常")
        else:
            print(f"  ⚠️  连接状态码: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")
        return False
    
    # 测试上传
    success, email = test_upload()
    
    if success:
        # 验证上传
        verify_upload(email)
        
        print_section("测试完成")
        print("  ✅ 上传和验证都成功！")
        print(f"\n  测试邮箱: {email}")
        print(f"  可以在浏览器中访问 dashboard 查看结果")
        return True
    else:
        print_section("测试失败")
        print("  ❌ 上传失败，请检查错误信息")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
