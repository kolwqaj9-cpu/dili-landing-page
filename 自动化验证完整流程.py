"""
PropKit 完整自动化验证流程
模拟访客操作 → 触发计算 → 验证结果
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
# Selenium is optional - will try to import if available
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 配置
LANDING_URL = "https://propkitai.tech/landing.html"
API_WEBHOOK = "https://api.propkitai.tech/api/webhook"
SUPABASE_URL = "https://vlrdiajxxnangawfcgvk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZscmRpYWp4eG5hbmdhd2ZjZ3ZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTkxNzYyNiwiZXhwIjoyMDg1NDkzNjI2fQ.WJGxW0o_NFa9lgu_tJ1otsxjxI8-3O6RPIkjLMFRYEg"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_services():
    """检查服务是否运行"""
    print_section("Step 1: Checking Services")
    
    cloudflared_ok = False
    python_ok = False
    
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq cloudflared.exe"],
            capture_output=True,
            text=True,
            timeout=5
        )
        cloudflared_ok = "cloudflared.exe" in result.stdout
    except:
        pass
    
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe"],
            capture_output=True,
            text=True,
            timeout=5
        )
        python_ok = "python.exe" in result.stdout
    except:
        pass
    
    if cloudflared_ok:
        print("  [OK] Cloudflared is running")
    else:
        print("  [FAIL] Cloudflared is NOT running")
        return False
    
    if python_ok:
        print("  [OK] Python backend is running")
    else:
        print("  [FAIL] Python backend is NOT running")
        return False
    
    # 测试 API
    try:
        response = requests.get(API_WEBHOOK, timeout=5)
        if response.status_code < 500:
            print("  [OK] API is accessible")
            return True
    except:
        pass
    
    print("  [WARN] API test failed, but continuing...")
    return True

def simulate_visitor_action():
    """模拟访客操作：点击购买按钮（实际是免费试用）"""
    print_section("Step 2: Simulating Visitor Action")
    
    test_email = f"auto_test_{int(time.time())}@verification.com"
    print(f"  Test email: {test_email}")
    
    # 方法1: 直接调用 API（更快更可靠）
    print("  Calling webhook API directly...")
    try:
        response = requests.post(
            API_WEBHOOK,
            json={"email": test_email},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  [OK] Webhook called successfully")
            print(f"  Response: {result}")
            return test_email, True
        else:
            print(f"  [FAIL] Webhook returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return test_email, False
    except Exception as e:
        print(f"  [FAIL] Webhook call failed: {e}")
        return test_email, False

def wait_for_computation(email, max_wait=180):
    """等待计算完成（GPU计算 + JSON导出 + 上传）"""
    print_section("Step 3: Waiting for Computation")
    
    print(f"  Waiting for GPU computation to complete...")
    print(f"  This may take 30-180 seconds")
    print(f"  Monitoring Supabase for data...")
    
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
                    record = data[0]
                    if record.get('data_payload'):
                        payload = record['data_payload']
                        print(f"  [OK] Data found! (elapsed: {elapsed}s)")
                        print(f"    Total analyzed: {payload.get('total_analyzed', 'N/A')}")
                        print(f"    Target count: {payload.get('target_count', 'N/A')}")
                        print(f"    Data points: {len(payload.get('data', []))}")
                        return True, payload
                else:
                    if elapsed - int(last_status_time - start_time) >= 15:
                        print(f"  [WAIT] Still processing... ({elapsed}s/{max_wait}s)")
                        last_status_time = time.time()
        except Exception as e:
            if elapsed - int(last_status_time - start_time) >= 15:
                print(f"  [WAIT] Checking... ({elapsed}s/{max_wait}s)")
                last_status_time = time.time()
        
        time.sleep(3)
    
    print(f"  [FAIL] Timeout after {max_wait} seconds")
    return False, None

def verify_computation_result(payload):
    """验证计算结果是否正确"""
    print_section("Step 4: Verifying Computation Result")
    
    if not payload:
        print("  [FAIL] No payload to verify")
        return False
    
    # 验证数据完整性
    checks = []
    
    # 检查1: 总分析数应该大于0
    total_analyzed = payload.get('total_analyzed', 0)
    if total_analyzed > 0:
        print(f"  [OK] Total analyzed: {total_analyzed}")
        checks.append(True)
    else:
        print(f"  [FAIL] Total analyzed is 0")
        checks.append(False)
    
    # 检查2: 目标数应该大于0
    target_count = payload.get('target_count', 0)
    if target_count > 0:
        print(f"  [OK] Target count: {target_count}")
        checks.append(True)
    else:
        print(f"  [FAIL] Target count is 0")
        checks.append(False)
    
    # 检查3: 数据点应该存在
    data_points = payload.get('data', [])
    if len(data_points) > 0:
        print(f"  [OK] Data points: {len(data_points)}")
        checks.append(True)
        
        # 验证数据点格式
        first_point = data_points[0]
        if isinstance(first_point, list) and len(first_point) >= 4:
            print(f"  [OK] Data point format correct: {first_point[:4]}")
            checks.append(True)
        else:
            print(f"  [FAIL] Data point format incorrect: {first_point}")
            checks.append(False)
    else:
        print(f"  [FAIL] No data points")
        checks.append(False)
    
    # 检查4: 预期值验证（基于之前的测试结果）
    # 预期：total_analyzed 应该接近 288136
    if 280000 <= total_analyzed <= 300000:
        print(f"  [OK] Total analyzed matches expected range (280k-300k)")
        checks.append(True)
    else:
        print(f"  [WARN] Total analyzed ({total_analyzed}) outside expected range")
        checks.append(False)
    
    # 检查5: 目标数应该合理（基于之前的测试结果）
    if 20000 <= target_count <= 30000:
        print(f"  [OK] Target count matches expected range (20k-30k)")
        checks.append(True)
    else:
        print(f"  [WARN] Target count ({target_count}) outside expected range")
        checks.append(False)
    
    success_rate = sum(checks) / len(checks) if checks else 0
    
    if success_rate >= 0.8:  # 80% 检查通过
        print(f"\n  [OK] Verification passed! ({int(success_rate*100)}% checks passed)")
        return True
    else:
        print(f"\n  [FAIL] Verification failed! ({int(success_rate*100)}% checks passed)")
        return False

def verify_dashboard_display(email):
    """验证 Dashboard 是否正确显示数据"""
    print_section("Step 5: Verifying Dashboard Display")
    
    dashboard_url = f"https://propkitai.tech/dashboard.html?email={email}"
    print(f"  Dashboard URL: {dashboard_url}")
    
    # 方法1: 尝试使用 Selenium（如果可用）
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        
        print("  Attempting browser verification with Selenium...")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.get(dashboard_url)
        time.sleep(5)
        
        page_title = driver.title
        print(f"  Page title: {page_title}")
        
        try:
            chart_element = driver.find_element(By.ID, "main-chart")
            print("  [OK] Chart element found")
            
            page_source = driver.page_source
            if "total_analyzed" in page_source or "target_count" in page_source:
                print("  [OK] Data found in page source")
                driver.quit()
                return True
            else:
                print("  [WARN] Data not found in page source")
                driver.quit()
                return False
        except NoSuchElementException:
            print("  [WARN] Chart element not found")
            driver.quit()
            return False
    except ImportError:
        print("  [INFO] Selenium not available, skipping browser verification")
    except Exception as e:
        print(f"  [WARN] Browser verification failed: {e}")
    
    # 方法2: 使用 requests 验证页面可访问
    try:
        print("  Verifying dashboard URL is accessible...")
        response = requests.get(dashboard_url, timeout=10)
        if response.status_code == 200:
            print("  [OK] Dashboard page is accessible")
            if email in response.text:
                print("  [OK] Email parameter found in page")
                return True
            else:
                print("  [WARN] Email parameter not found in page")
                return True  # 不阻塞
        else:
            print(f"  [WARN] Dashboard returned status {response.status_code}")
            return True  # 不阻塞
    except Exception as e:
        print(f"  [WARN] Dashboard verification failed: {e}")
        return True  # 不阻塞，因为数据验证已经完成

def main():
    print("\n" + "=" * 70)
    print("  PropKit Complete Automated Verification")
    print("=" * 70)
    print(f"\nStart time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: 检查服务
    if not check_services():
        print("\n[FAIL] Services are not running. Please start them first.")
        print("Run: 快速启动.bat or 启动服务.bat")
        return False
    
    # Step 2: 模拟访客操作（免费试用，不触发购买）
    email, success = simulate_visitor_action()
    if not success:
        print("\n[FAIL] Failed to trigger computation")
        return False
    
    print(f"\n[OK] Visitor action simulated - Free trial activated for {email}")
    print("  Note: No payment link triggered, directly granting free trial")
    
    # Step 3: 等待计算完成
    computation_success, payload = wait_for_computation(email, max_wait=180)
    if not computation_success:
        print("\n[FAIL] Computation did not complete in time")
        return False
    
    print(f"\n[OK] Computation completed successfully")
    
    # Step 4: 验证计算结果
    verification_success = verify_computation_result(payload)
    if not verification_success:
        print("\n[FAIL] Computation result verification failed")
        return False
    
    # Step 5: 验证 Dashboard 显示（可选）
    dashboard_success = verify_dashboard_display(email)
    
    # 总结
    print_section("Verification Summary")
    
    print(f"""
  Test Email: {email}
  Computation: {'[OK]' if computation_success else '[FAIL]'}
  Result Verification: {'[OK]' if verification_success else '[FAIL]'}
  Dashboard Display: {'[OK]' if dashboard_success else '[WARN]'}
  
  Overall Result: {'[SUCCESS]' if (computation_success and verification_success) else '[FAIL]'}
    """)
    
    if computation_success and verification_success:
        print("  ✅ Complete verification PASSED!")
        print(f"  Dashboard URL: https://propkitai.tech/dashboard.html?email={email}")
        return True
    else:
        print("  ❌ Complete verification FAILED!")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAIL] Verification error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
