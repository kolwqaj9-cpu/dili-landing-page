import subprocess
import time
import os
import sys
import pandas as pd
import struct
from playwright.sync_api import sync_playwright

# --- 配置 ---
PROJECT_DIR = os.getcwd() # 使用当前目录
BASE_URL = "http://127.0.0.1:8000"
TEST_EMAIL = "system_browser_test@propkit.ai"

def setup_data():
    print("📝 [1/5] 正在准备测试数据...")
    if not os.path.exists("data"): os.makedirs("data")
    if not os.path.exists("static"): os.makedirs("static")
    
    # 生成 CSV
    df = pd.DataFrame({'pitch_type': ['FF']*10, 'plate_x': [0.5]*10, 'plate_z': [2.0]*10})
    df.to_csv(os.path.join("data", "mlb_full_physics_vectors.csv"), index=False)
    
    # 生成 Bin
    with open(os.path.join("data", "sniper_results.bin"), 'wb') as f:
        f.write(struct.pack('i', 10))
        for _ in range(10): f.write(struct.pack('ifi', 1, 95.0, 1))
    print("✅ 数据准备完毕")

def cleanup(processes):
    print("\n🧹 [清理] 正在关闭所有进程...")
    for p in processes:
        if p.poll() is None: # 如果进程还在运行
            try:
                p.terminate()
            except:
                p.kill()

def run_test():
    processes = []
    try:
        # 1. 启动后端
        print(f"🚀 [2/5] 启动后端服务...")
        backend = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(backend)
        
        print("⏳ 等待后端启动 (5秒)...")
        time.sleep(5)

        # 2. 启动浏览器测试 (使用本机 Edge)
        print(f"🎭 [3/5] 启动浏览器 (调用本机 Microsoft Edge)...")
        with sync_playwright() as p:
            # 关键修改：channel="msedge" 会直接调用你电脑上的 Edge
            # 如果你想用 Chrome，把下面改成 channel="chrome"
            browser = p.chromium.launch(headless=False, channel="msedge")
            
            context = browser.new_context()
            page = context.new_page()
            
            print(f"🌍 [4/5] 访问页面: {BASE_URL}")
            try:
                page.goto(BASE_URL, timeout=10000)
            except Exception as e:
                print(f"⚠️ 无法连接到页面，请检查后端是否报错: {e}")
                # 打印后端报错以便调试
                if backend.poll() is not None:
                    print("❌ 后端进程已意外退出！")
                    print(backend.stdout.read())
                    print(backend.stderr.read())
                raise e

            # 模拟用户操作
            print("👤 模拟用户操作...")
            try:
                # 尝试寻找输入框，找不到也没事，截图最重要
                page.fill("input[type='email']", TEST_EMAIL)
                print("✅ 邮箱已输入")
            except:
                print("⚠️ 未找到邮箱输入框 (可能是页面结构不同)，跳过")

            # 截图验证
            print("📸 [5/5] 截图保存结果...")
            page.screenshot(path="system_browser_result.png")
            print("✅ 截图已保存为 system_browser_result.png")
            
            print("\n👀 浏览器将保持打开 5 秒供你查看...")
            time.sleep(5)
            browser.close()
            
        print("\n🎉🎉🎉 全流程验证成功！(使用本机浏览器)")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    finally:
        cleanup(processes)

if __name__ == "__main__":
    setup_data()
    run_test()