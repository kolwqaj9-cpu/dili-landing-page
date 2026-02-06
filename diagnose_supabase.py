"""
Supabase 数据库诊断脚本
用于检查连接、表结构和数据
"""

import requests
import json
from datetime import datetime

# 从 main.py 读取配置（请确保这些值正确）
S_URL = "https://vlrdiajxxnangawfcgvk.supabase.co"
S_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZscmRpYWp4eG5hbmdhd2ZjZ3ZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTkxNzYyNiwiZXhwIjoyMDg1NDkzNjI2fQ.WJGxW0o_NFa9lgu_tJ1otsxjxI8-3O6RPIkjLMFRYEg"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_connection():
    """测试 Supabase 连接"""
    print_section("1. 测试 Supabase 连接")
    
    try:
        # 测试基本连接
        response = requests.get(
            f"{S_URL}/rest/v1/",
            headers={
                "apikey": S_KEY,
                "Authorization": f"Bearer {S_KEY}"
            },
            timeout=10
        )
        print(f"  ✅ 连接成功 (状态码: {response.status_code})")
        return True
    except Exception as e:
        print(f"  ❌ 连接失败: {e}")
        return False

def check_table_structure():
    """检查 reports 表结构"""
    print_section("2. 检查 reports 表结构")
    
    try:
        # 尝试查询表（不返回数据，只检查表是否存在）
        response = requests.get(
            f"{S_URL}/rest/v1/reports?limit=0",
            headers={
                "apikey": S_KEY,
                "Authorization": f"Bearer {S_KEY}",
                "Prefer": "count=exact"
            },
            timeout=10
        )
        
        if response.status_code in [200, 206]:  # 206 是部分内容，也是正常的
            print("  ✅ reports 表存在")
            print(f"  状态码: {response.status_code} (正常)")
            
            # 尝试获取表信息
            if 'Content-Range' in response.headers:
                print(f"  表记录数: {response.headers.get('Content-Range', '未知')}")
            
            return True
        elif response.status_code == 404:
            print("  ❌ reports 表不存在")
            print("  需要在 Supabase 中创建 reports 表")
            return False
        else:
            print(f"  ⚠️  状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def list_all_tables():
    """列出所有表"""
    print_section("3. 尝试列出所有表")
    
    try:
        # Supabase REST API 不直接支持列出表，但我们可以尝试一些常见表名
        common_tables = ['reports', 'users', 'data', 'analytics']
        
        for table in common_tables:
            try:
                response = requests.get(
                    f"{S_URL}/rest/v1/{table}?limit=0",
                    headers={
                        "apikey": S_KEY,
                        "Authorization": f"Bearer {S_KEY}"
                    },
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"  ✅ 表 '{table}' 存在")
                elif response.status_code == 404:
                    print(f"  ❌ 表 '{table}' 不存在")
            except:
                pass
    except Exception as e:
        print(f"  ⚠️  无法列出表: {e}")

def check_existing_data():
    """检查现有数据"""
    print_section("4. 检查现有数据")
    
    try:
        response = requests.get(
            f"{S_URL}/rest/v1/reports?select=*&order=id.desc&limit=5",
            headers={
                "apikey": S_KEY,
                "Authorization": f"Bearer {S_KEY}",
                "Prefer": "count=exact"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 查询成功")
            print(f"  找到 {len(data)} 条记录")
            
            if len(data) > 0:
                print("\n  最近的记录:")
                for i, record in enumerate(data[:3], 1):
                    print(f"\n  记录 {i}:")
                    print(f"    ID: {record.get('id', 'N/A')}")
                    print(f"    Email: {record.get('user_email', 'N/A')}")
                    print(f"    创建时间: {record.get('created_at', 'N/A (字段可能不存在)')}")
                    if record.get('data_payload'):
                        payload = record['data_payload']
                        print(f"    数据: total_analyzed={payload.get('total_analyzed', 'N/A')}, "
                              f"target_count={payload.get('target_count', 'N/A')}")
                    else:
                        print(f"    数据: 无 payload")
            else:
                print("  ⚠️  表中没有数据")
            
            return True
        else:
            print(f"  ❌ 查询失败 (状态码: {response.status_code})")
            print(f"  响应: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_insert():
    """测试插入数据"""
    print_section("5. 测试插入数据")
    
    test_email = f"diagnostic_test_{int(datetime.now().timestamp())}@test.com"
    test_data = {
        "user_email": test_email,
        "data_payload": {
            "total_analyzed": 100,
            "target_count": 10,
            "top_reason": 1,
            "data": [[1.0, 2.0, 0.95, 1]]
        }
    }
    
    try:
        response = requests.post(
            f"{S_URL}/rest/v1/reports",
            json=test_data,
            headers={
                "apikey": S_KEY,
                "Authorization": f"Bearer {S_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"  ✅ 插入成功")
            print(f"  测试邮箱: {test_email}")
            print(f"  响应: {response.json()}")
            return True
        else:
            print(f"  ❌ 插入失败 (状态码: {response.status_code})")
            print(f"  响应: {response.text[:500]}")
            
            # 常见错误提示
            if response.status_code == 400:
                print("\n  💡 可能的原因:")
                print("    - 表结构不匹配")
                print("    - 字段类型错误")
                print("    - 缺少必需字段")
            elif response.status_code == 401:
                print("\n  💡 可能的原因:")
                print("    - API Key 无效")
                print("    - 权限不足")
            
            return False
    except Exception as e:
        print(f"  ❌ 插入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_query_by_email():
    """测试按邮箱查询"""
    print_section("6. 测试按邮箱查询（这是 dashboard 使用的查询方式）")
    
    # 使用一个测试邮箱
    test_email = "test@example.com"
    
    try:
        response = requests.get(
            f"{S_URL}/rest/v1/reports?user_email=eq.{test_email}&order=id.desc&limit=1",
            headers={
                "apikey": S_KEY,
                "Authorization": f"Bearer {S_KEY}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 查询成功")
            print(f"  查询邮箱: {test_email}")
            print(f"  找到 {len(data)} 条记录")
            
            if len(data) > 0:
                print(f"  最新记录: {data[0]}")
            else:
                print("  ⚠️  该邮箱没有数据（这是正常的，如果这是测试邮箱）")
            
            return True
        else:
            print(f"  ❌ 查询失败 (状态码: {response.status_code})")
            print(f"  响应: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"  ❌ 查询失败: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  Supabase 数据库诊断工具")
    print("=" * 60)
    print(f"\nSupabase URL: {S_URL}")
    print(f"API Key: {S_KEY[:20]}...{S_KEY[-10:]}")
    
    results = {}
    
    # 运行所有检查
    results['connection'] = test_connection()
    results['table'] = check_table_structure()
    list_all_tables()
    results['data'] = check_existing_data()
    results['insert'] = test_insert()
    results['query'] = check_query_by_email()
    
    # 总结
    print_section("诊断总结")
    
    print("\n检查结果:")
    for check, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {check}: {status}")
    
    print("\n" + "=" * 60)
    print("  下一步操作建议")
    print("=" * 60)
    
    if not results['connection']:
        print("\n❌ 连接失败")
        print("  1. 检查 Supabase URL 是否正确")
        print("  2. 检查网络连接")
        print("  3. 检查 API Key 是否有效")
    
    if not results['table'] and results['data']:
        print("\n⚠️  表结构检查显示异常，但数据查询正常")
        print("  这可能是正常的（状态码206表示部分内容）")
        print("  如果数据查询、插入、按邮箱查询都通过，说明表结构正常")
    
    if not results['table'] and not results['data']:
        print("\n❌ 表结构问题")
        print("  表存在但可能缺少 created_at 字段")
        print("  解决方案:")
        print("    1. 在 Supabase SQL Editor 中执行 fix_supabase_table.sql")
        print("    2. 或运行: ALTER TABLE reports ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();")
    
    if not results['insert']:
        print("\n❌ 无法插入数据")
        print("  1. 检查表结构是否正确")
        print("  2. 检查字段类型是否匹配")
        print("  3. 检查 RLS (Row Level Security) 策略")
    
    if results['connection'] and results['data'] and results['insert'] and results['query']:
        print("\n✅ 所有关键检查通过！")
        print("  数据库配置正常，可以运行完整验证")
        print("\n  下一步:")
        print("  1. 确保服务运行: .\\一键启动.bat")
        print("  2. 运行完整验证: C:\\ProgramData\\Anaconda3\\python.exe e2e_full_verification.py")
        print("  3. 或浏览器测试: https://propkitai.tech/landing.html")
    
    if results['connection'] and results['table'] and results['insert']:
        print("\n✅ 所有基本检查通过！")
        print("  如果验证脚本仍然失败，可能是:")
        print("  1. GPU 计算时间较长（超过120秒）")
        print("  2. export_json.py 执行失败")
        print("  3. 数据生成但上传失败")
        print("\n  建议:")
        print("  - 检查 Python 后端的日志输出")
        print("  - 检查 static/tactical_data.json 是否生成")
        print("  - 增加验证脚本的等待时间")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  诊断被中断")
    except Exception as e:
        print(f"\n\n❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
