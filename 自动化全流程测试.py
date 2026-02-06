"""
PropKit 自动化全流程测试
包括：启动服务、等待就绪、浏览器测试、验证结果
"""

import os
import sys
import time
import subprocess
import requests
import webbrowser
from datetime import datetime

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def kill_existing_processes():
    """关闭现有进程"""
    print_section("Step 1: Cleaning Up")
    
    processes = ["cloudflared.exe", "python.exe"]
    for proc in processes:
        try:
            subprocess.run(["taskkill", "/F", "/IM", proc], 
                         capture_output=True, timeout=5)
            print(f"  [OK] Killed {proc}")
        except:
            pass
    
    time.sleep(2)

def start_cloudflared():
    """启动 Cloudflared"""
    print_section("Step 2: Starting Cloudflared")
    
    project_path = os.getcwd()
    exe_path = os.path.join(project_path, "cloudflared.exe")
    config_path = os.path.join(project_path, "config.yml")
    
    if not os.path.exists(exe_path):
        print(f"  [FAIL] cloudflared.exe not found")
        return False
    
    try:
        subprocess.Popen(
            [exe_path, "tunnel", "--config", config_path, "run", "3090-Home"],
            cwd=project_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print(f"  [OK] Cloudflared started")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to start Cloudflared: {e}")
        return False

def start_python_backend():
    """启动 Python 后端"""
    print_section("Step 3: Starting Python Backend")
    
    project_path = os.getcwd()
    python_exe = r"C:\ProgramData\Anaconda3\python.exe"
    
    if not os.path.exists(python_exe):
        python_exe = "python"
    
    main_py = os.path.join(project_path, "main.py")
    
    if not os.path.exists(main_py):
        print(f"  [FAIL] main.py not found")
        return False
    
    try:
        subprocess.Popen(
            [python_exe, "main.py"],
            cwd=project_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print(f"  [OK] Python backend started")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to start Python backend: {e}")
        return False

def wait_for_services(max_wait=30):
    """等待服务就绪"""
    print_section("Step 4: Waiting for Services")
    
    print(f"  Waiting up to {max_wait} seconds...")
    
    for i in range(max_wait):
        # 检查进程
        cloudflared_running = False
        python_running = False
        
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq cloudflared.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            cloudflared_running = "cloudflared.exe" in result.stdout
        except:
            pass
        
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            python_running = "python.exe" in result.stdout
        except:
            pass
        
        if cloudflared_running and python_running:
            # 测试 API
            try:
                response = requests.get(
                    "https://api.propkitai.tech/api/webhook",
                    timeout=3
                )
                if response.status_code < 500:
                    print(f"  [OK] Services are ready! ({i+1}s)")
                    return True
            except:
                pass
        
        if (i + 1) % 5 == 0:
            print(f"  Still waiting... ({i+1}s/{max_wait}s)")
        
        time.sleep(1)
    
    print(f"  [WARN] Timeout after {max_wait} seconds")
    return False

def open_browser():
    """打开浏览器"""
    print_section("Step 5: Opening Browser")
    
    url = "https://propkitai.tech/landing.html"
    
    try:
        webbrowser.open(url)
        print(f"  [OK] Browser opened: {url}")
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to open browser: {e}")
        return False

def print_test_instructions():
    """打印测试说明"""
    print_section("Test Instructions")
    
    print("""
  In the browser:
    1. Click "Request Access" button
    2. Enter email address (e.g., test_auto@example.com)
    3. Click "ACTIVATE FREE TRIAL"
  
  Watch the Python Backend window:
    - You should see: "⚡ [3090] 启动任务: [email]"
    - GPU computation will start
    - Wait for: "✅ 同步完成，状态码: 201"
  
  Browser will auto-redirect to dashboard:
    - Check if chart is displayed
    - Verify data statistics (Total Analyzed, Target Count)
  
  Expected timeline:
    - Webhook call: Immediate
    - GPU computation: 30-120 seconds
    - JSON export: 1-2 seconds
    - Supabase upload: 1-2 seconds
    - Dashboard display: Immediate after upload
    """)

def main():
    print("\n" + "=" * 60)
    print("  PropKit Automated Full Flow Test")
    print("=" * 60)
    print(f"\nStart time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Cleanup
    kill_existing_processes()
    
    # Step 2: Start Cloudflared
    if not start_cloudflared():
        print("\n[FAIL] Failed to start Cloudflared")
        return False
    
    # Step 3: Start Python Backend
    if not start_python_backend():
        print("\n[FAIL] Failed to start Python backend")
        return False
    
    # Step 4: Wait for services
    if not wait_for_services():
        print("\n[WARN] Services may not be fully ready, but continuing...")
    
    # Step 5: Open browser
    open_browser()
    
    # Print instructions
    print_test_instructions()
    
    print_section("Test Started")
    print("""
  Services are running in background console windows.
  Close those windows to stop services.
  
  Monitor the Python Backend window for processing logs.
  
  Test is now running in browser!
    """)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n[OK] Full flow test initiated successfully!")
            print("Press Enter to exit...")
            input()
        else:
            print("\n[FAIL] Full flow test failed to start")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
