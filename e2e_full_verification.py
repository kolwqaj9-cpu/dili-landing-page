"""
PropKit 端到端完整验证脚本
使用 Anaconda Python 环境进行完整流程验证
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime

# 配置
API_WEBHOOK = "https://api.propkitai.tech/api/webhook"
SUPABASE_URL = "https://vlrdiajxxnangawfcgvk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZscmRpYWp4eG5hbmdhd2ZjZ3ZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTkxNzYyNiwiZXhwIjoyMDg1NDkzNjI2fQ.WJGxW0o_NFa9lgu_tJ1otsxjxI8-3O6RPIkjLMFRYEg"

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def check_service(name, process_name, check_url=None):
    """检查服务是否运行"""
    print(f"\n[检查] {name}...")
    
    # 检查进程
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            is_running = process_name.lower() in result.stdout.lower()
        else:
            result = subprocess.run(
                ["pgrep", "-f", process_name],
                capture_output=True,
                timeout=5
            )
            is_running = result.returncode == 0
        
        if is_running:
            print(f"  ✅ {name} 进程运行中")
        else:
            print(f"  ❌ {name} 进程未运行")
            return False
    except Exception as e:
        print(f"  ⚠️  无法检查进程: {e}")
        return False
    
    # 如果提供了 URL，检查连接
    if check_url:
        try:
            response = requests.get(check_url, timeout=5)
            if response.status_code < 500:
                print(f"  ✅ {name} 服务可访问")
                return True
            else:
                print(f"  ⚠️  {name} 服务响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ {name} 服务不可访问: {e}")
            return False
    
    return True

def test_webhook(email):
    """测试 webhook API"""
    print(f"\n[测试] Webhook API...")
    print(f"  测试邮箱: {email}")
    
    try:
        response = requests.post(
            API_WEBHOOK,
            json={"email": email},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✅ Webhook 调用成功")
            print(f"  响应: {response.json()}")
            return True
        else:
            print(f"  ⚠️  Webhook 响应异常: {response.status_code}")
            print(f"  响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Webhook 调用失败: {e}")
        return False

def check_supabase_data(email, max_wait=120):
    """检查 Supabase 中的数据"""
    print(f"\n[检查] Supabase 数据...")
    print(f"  等待数据生成（最多 {max_wait} 秒）...")
    print(f"  查询邮箱: {email}")
    
    # 先测试连接
    try:
        test_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/reports?limit=0",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=5
        )
        if test_response.status_code != 200:
            print(f"  ❌ Supabase 连接失败 (状态码: {test_response.status_code})")
            print(f"  响应: {test_response.text[:200]}")
            print(f"\n  💡 建议:")
            print(f"    1. 运行诊断脚本: C:\\ProgramData\\Anaconda3\\python.exe diagnose_supabase.py")
            print(f"    2. 检查 Supabase URL 和 API Key 是否正确")
            return False
    except Exception as e:
        print(f"  ❌ Supabase 连接测试失败: {e}")
        print(f"\n  💡 建议运行诊断脚本检查配置")
        return False
    
    start_time = time.time()
    last_status_time = start_time
    
    while time.time() - start_time < max_wait:
        elapsed = int(time.time() - start_time)
        
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/reports?user_email=eq.{email}&order=id.desc&limit=1",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    report = data[0]
                    print(f"  ✅ 找到数据记录 (耗时: {elapsed}秒)")
                    print(f"  创建时间: {report.get('created_at', 'N/A')}")
                    
                    if report.get('data_payload'):
                        payload = report['data_payload']
                        print(f"  总分析数: {payload.get('total_analyzed', 0)}")
                        print(f"  目标数: {payload.get('target_count', 0)}")
                        print(f"  数据点: {len(payload.get('data', []))}")
                        return True
                    else:
                        print(f"  ⚠️  数据记录存在但 payload 为空")
                        return True  # 至少找到了记录
                else:
                    # 每10秒显示一次状态
                    if elapsed - int(last_status_time - start_time) >= 10:
                        print(f"  ⏳ 数据尚未生成，等待中... ({elapsed}s/{max_wait}s)")
                        print(f"     提示: GPU计算可能需要较长时间")
                        last_status_time = time.time()
            elif response.status_code == 400:
                print(f"  ❌ 查询语法错误 (状态码: 400)")
                print(f"  响应: {response.text[:200]}")
                print(f"  可能是邮箱格式问题或表结构不匹配")
                return False
            elif response.status_code == 401:
                print(f"  ❌ 认证失败 (状态码: 401)")
                print(f"  请检查 Supabase API Key 是否正确")
                return False
            else:
                if elapsed - int(last_status_time - start_time) >= 10:
                    print(f"  ⚠️  Supabase 查询失败: {response.status_code} (等待中... {elapsed}s)")
                    last_status_time = time.time()
        
        except requests.exceptions.Timeout:
            if elapsed - int(last_status_time - start_time) >= 10:
                print(f"  ⚠️  查询超时 (等待中... {elapsed}s)")
                last_status_time = time.time()
        except Exception as e:
            if elapsed - int(last_status_time - start_time) >= 10:
                print(f"  ⚠️  查询错误: {e} (等待中... {elapsed}s)")
                last_status_time = time.time()
        
        time.sleep(3)
    
    print(f"\n  ❌ 超时：{max_wait} 秒内未找到数据")
    print(f"\n  💡 可能的原因:")
    print(f"    1. GPU 计算时间超过 {max_wait} 秒")
    print(f"    2. export_json.py 执行失败")
    print(f"    3. 数据上传到 Supabase 失败")
    print(f"    4. 邮箱地址不匹配")
    print(f"\n  💡 建议:")
    print(f"    1. 检查 Python 后端窗口的日志输出")
    print(f"    2. 检查 static/tactical_data.json 是否生成")
    print(f"    3. 运行诊断脚本: C:\\ProgramData\\Anaconda3\\python.exe diagnose_supabase.py")
    print(f"    4. 检查 Supabase Dashboard 中是否有数据")
    
    return False

def check_files():
    """检查必要文件"""
    print(f"\n[检查] 必要文件...")
    
    required_files = [
        "landing.html",
        "dashboard.html",
        "main.py",
        "config.yml",
        "export_json.py"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} 缺失")
            all_exist = False
    
    return all_exist

def main():
    """主函数"""
    print_section("PropKit 端到端验证")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查文件
    if not check_files():
        print("\n❌ 必要文件缺失，请检查项目目录")
        return False
    
    # 2. 检查服务
    print_section("服务状态检查")
    cloudflared_ok = check_service("Cloudflared", "cloudflared")
    python_ok = check_service("Python", "python")
    
    if not cloudflared_ok:
        print("\n⚠️  请先启动 Cloudflared:")
        print("  cloudflared tunnel --config config.yml run 3090-Home")
    
    if not python_ok:
        print("\n⚠️  请先启动 Python 后端:")
        print("  C:\\ProgramData\\Anaconda3\\python.exe main.py")
    
    if not (cloudflared_ok and python_ok):
        print("\n❌ 服务未完全启动，无法继续验证")
        return False
    
    # 3. 测试 API
    print_section("API 连接测试")
    test_email = f"test_{int(time.time())}@verification.com"
    
    if not test_webhook(test_email):
        print("\n❌ Webhook 测试失败")
        return False
    
    # 4. 检查数据生成（增加等待时间到120秒）
    print_section("数据生成验证")
    print("注意: GPU 计算可能需要较长时间，请耐心等待...")
    if check_supabase_data(test_email, max_wait=120):
        print("\n✅ 端到端验证成功！")
        print(f"\n测试邮箱: {test_email}")
        print(f"Dashboard 链接: https://propkitai.tech/dashboard.html?email={test_email}")
        return True
    else:
        print("\n⚠️  数据生成验证失败")
        print("可能原因:")
        print("  1. GPU 计算时间较长")
        print("  2. export_json.py 执行失败")
        print("  3. Supabase 同步失败")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
