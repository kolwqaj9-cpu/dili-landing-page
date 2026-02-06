#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动配置 Vercel 环境变量脚本
使用 Playwright 自动化浏览器操作
使用 Chrome 用户数据目录保持登录状态
"""

import time
import json
import os
from playwright.sync_api import sync_playwright

# ==================== 配置数据 ====================
SUPABASE_URL = "https://bmwfnuekfgolwutnffmf.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJtd2ZudWVrZmdvbHd1dG5mZm1mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDM1MjIxMywiZXhwIjoyMDg1OTI4MjEzfQ.lYmpk8t9MNiHAqmul6vnT6x_oqCrxcbXN9xgyTKTFPA"

VERCEL_ENV_VARS_URL = "https://vercel.com/wu-zhihais-projects/baseprops/settings/environment-variables"
VERCEL_DEPLOYMENTS_URL = "https://vercel.com/wu-zhihais-projects/baseprops/deployments"
API_CHECK_URL = "https://baseprops.vercel.app/api/stats/purchases"

# Chrome 用户数据目录路径
CHROME_USER_DATA_DIR = "C:/Users/Administrator/AppData/Local/Google/Chrome/User Data"
# =================================================

def print_step(msg):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"[步骤] {msg}")
    print(f"{'='*60}\n")

def find_chrome_user_data():
    """查找 Chrome 用户数据目录"""
    possible_paths = [
        "C:/Users/Administrator/AppData/Local/Google/Chrome/User Data",
        os.path.expanduser("~/AppData/Local/Google/Chrome/User Data"),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google/Chrome/User Data'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"[INFO] 找到 Chrome 用户数据目录: {path}")
            return path
    
    print("[WARN] 未找到 Chrome 用户数据目录，将使用默认路径")
    return possible_paths[0]

def main():
    print_step("开始自动配置 Vercel 环境变量")
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Service Role Key: {SERVICE_ROLE_KEY[:50]}...")
    print()
    
    # 查找 Chrome 用户数据目录
    user_data_dir = find_chrome_user_data()
    
    print("[WARN] 重要提示：")
    print("1. 请先关闭所有 Chrome 浏览器窗口")
    print("2. 确保 Chrome 完全退出（检查任务管理器）")
    print("3. 脚本将在 3 秒后自动继续...")
    import time
    time.sleep(3)
    
    with sync_playwright() as p:
        # 使用 launch_persistent_context 启动浏览器（保持登录状态）
        print_step("启动浏览器（使用 Chrome 用户数据目录）")
        print(f"用户数据目录: {user_data_dir}")
        print("这将保持您的登录状态（Gmail、GitHub、Vercel）")
        
        try:
            # 检查 Chrome 是否正在运行
            import subprocess
            chrome_running = False
            try:
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                if 'chrome.exe' in result.stdout:
                    chrome_running = True
                    print("[ERROR] 检测到 Chrome 正在运行！")
                    print("请先关闭所有 Chrome 窗口，然后重新运行脚本")
                    print("或者等待脚本自动尝试（可能会失败）...")
                    print()
            except:
                pass
            
            # 尝试使用普通启动方式（如果 persistent_context 失败）
            print("[INFO] 尝试启动浏览器...")
            try:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False,
                    slow_mo=500,
                    channel="chrome",
                    timeout=60000,  # 60秒超时
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--remote-debugging-port=9222',  # 添加调试端口
                    ]
                )
            except Exception as e:
                print(f"[WARN] 使用用户数据目录失败: {str(e)[:100]}")
                print("[INFO] 改用普通启动方式（需要手动登录）...")
                browser = p.chromium.launch(headless=False, slow_mo=500, channel="chrome")
                context = browser.new_context()
                print("[INFO] 浏览器已启动，请手动登录 Vercel（如果需要）")
                print("[INFO] 等待 10 秒...")
                time.sleep(10)
            page = context.new_page()
            
            # 步骤 1: 直接导航到环境变量设置页面（跳过登录）
            print_step("导航到 Vercel 环境变量设置页面")
            print(f"URL: {VERCEL_ENV_VARS_URL}")
            page.goto(VERCEL_ENV_VARS_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)  # 等待页面完全加载
            
            # 步骤 2: 查找并编辑 SUPABASE_SERVICE_ROLE_KEY 变量
            print_step("查找 SUPABASE_SERVICE_ROLE_KEY 环境变量")
            
            # 等待环境变量列表加载
            page.wait_for_timeout(2000)
            
            # 查找包含 SUPABASE_SERVICE_ROLE_KEY 的行
            print("正在查找环境变量行...")
            
            # 方法1: 通过文本查找变量名
            key_found = False
            try:
                # 查找包含 "SUPABASE_SERVICE_ROLE_KEY" 的元素
                key_locator = page.locator('text=SUPABASE_SERVICE_ROLE_KEY').first
                if key_locator.count() > 0:
                    print("[OK] 找到 SUPABASE_SERVICE_ROLE_KEY 变量")
                    key_found = True
                    
                    # 在同一行或父元素中查找 Edit 按钮
                    # 尝试多种方式定位 Edit 按钮
                    edit_selectors = [
                        'button:has-text("Edit")',
                        'button[aria-label*="Edit"]',
                        'a:has-text("Edit")',
                        '//button[contains(text(), "Edit")]',
                    ]
                    
                    edit_button = None
                    for selector in edit_selectors:
                        try:
                            edit_button = page.locator(selector).first
                            if edit_button.count() > 0:
                                # 检查是否在同一个表格行中
                                key_element = key_locator.first
                                edit_element = edit_button.first
                                
                                # 获取它们的位置，如果距离较近，可能是同一行
                                key_box = key_element.bounding_box()
                                edit_box = edit_button.bounding_box()
                                
                                if key_box and edit_box:
                                    # 如果垂直位置相近（同一行），使用它
                                    if abs(key_box['y'] - edit_box['y']) < 50:
                                        print(f"[OK] 找到 Edit 按钮: {selector}")
                                        break
                        except:
                            continue
                    
                    if edit_button and edit_button.count() > 0:
                        print_step("点击 Edit 按钮")
                        edit_button.click()
                        page.wait_for_timeout(2000)
                    else:
                        print("[WARN] 无法自动找到 Edit 按钮")
                        print("请手动点击 SUPABASE_SERVICE_ROLE_KEY 行的 Edit 按钮")
                        print("等待 15 秒...")
                        page.wait_for_timeout(15000)
            except Exception as e:
                print(f"[WARN] 查找变量时出错: {e}")
                print("请手动找到 SUPABASE_SERVICE_ROLE_KEY 并点击 Edit")
                print("等待 15 秒...")
                page.wait_for_timeout(15000)
            
            # 步骤 3: 清空旧值并输入新值
            print_step("更新环境变量值")
            
            # 查找输入框
            value_input = None
            input_selectors = [
                'textarea[name*="value"]',
                'input[name*="value"]',
                'textarea[placeholder*="value"]',
                'input[placeholder*="value"]',
                'textarea',
                'input[type="text"]',
                '//textarea',
                '//input[@type="text"]',
            ]
            
            for selector in input_selectors:
                try:
                    value_input = page.locator(selector).first
                    if value_input.count() > 0:
                        # 检查是否可见
                        if value_input.is_visible():
                            print(f"[OK] 找到输入框: {selector}")
                            break
                except:
                    continue
            
            if value_input and value_input.count() > 0 and value_input.is_visible():
                print("清空旧值...")
                value_input.click()
                page.wait_for_timeout(300)
                value_input.fill('')  # 清空
                page.wait_for_timeout(500)
                
                print("输入新值...")
                value_input.fill(SERVICE_ROLE_KEY)
                page.wait_for_timeout(1000)
                print("[OK] 新值已输入")
            else:
                print("[WARN] 无法自动找到输入框")
                print(f"请手动输入新值: {SERVICE_ROLE_KEY}")
                print("等待 15 秒，请手动操作...")
                page.wait_for_timeout(15000)
            
            # 步骤 4: 保存
            print_step("保存更改")
            save_selectors = [
                'button:has-text("Save")',
                'button:has-text("保存")',
                'button[type="submit"]',
                '//button[contains(text(), "Save")]',
            ]
            
            save_button = None
            for selector in save_selectors:
                try:
                    save_button = page.locator(selector).first
                    if save_button.count() > 0 and save_button.is_visible():
                        print(f"[OK] 找到保存按钮: {selector}")
                        break
                except:
                    continue
            
            if save_button and save_button.count() > 0:
                save_button.click()
                print("[OK] 已点击保存按钮")
                page.wait_for_timeout(3000)
            else:
                print("[WARN] 无法自动找到保存按钮")
                print("请手动点击保存按钮")
                print("等待 5 秒...")
                page.wait_for_timeout(5000)
            
            # 步骤 5: 跳转到 Deployments 页面并触发 Redeploy
            print_step("跳转到 Deployments 页面")
            page.goto(VERCEL_DEPLOYMENTS_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            print_step("查找最新部署的 Redeploy 按钮")
            
            # 查找 Redeploy 按钮
            redeploy_button = None
            redeploy_selectors = [
                'button:has-text("Redeploy")',
                'a:has-text("Redeploy")',
                'button[aria-label*="Redeploy"]',
                '//button[contains(text(), "Redeploy")]',
                '//a[contains(text(), "Redeploy")]',
            ]
            
            for selector in redeploy_selectors:
                try:
                    redeploy_button = page.locator(selector).first
                    if redeploy_button.count() > 0 and redeploy_button.is_visible():
                        print(f"[OK] 找到 Redeploy 按钮: {selector}")
                        break
                except:
                    continue
            
            if redeploy_button and redeploy_button.count() > 0:
                print("点击 Redeploy 按钮...")
                redeploy_button.click()
                page.wait_for_timeout(2000)
                
                # 确认 Redeploy（如果有确认对话框）
                confirm_selectors = [
                    'button:has-text("Redeploy")',
                    'button:has-text("Confirm")',
                    'button:has-text("确认")',
                ]
                
                for selector in confirm_selectors:
                    try:
                        confirm_button = page.locator(selector).first
                        if confirm_button.count() > 0 and confirm_button.is_visible():
                            confirm_button.click()
                            print("[OK] 已确认 Redeploy")
                            break
                    except:
                        continue
            else:
                print("[WARN] 无法自动找到 Redeploy 按钮")
                print("请手动点击最新部署的 Redeploy 按钮")
                print("等待 15 秒...")
                page.wait_for_timeout(15000)
            
            # 步骤 6: 等待部署完成
            print_step("等待部署完成...")
            print("这可能需要 1-2 分钟，请耐心等待...")
            
            # 等待部署状态变为 Ready（最多等待 2 分钟）
            max_wait = 120  # 2分钟
            waited = 0
            while waited < max_wait:
                page.wait_for_timeout(5000)  # 每5秒检查一次
                waited += 5
                print(f"已等待 {waited} 秒...")
                
                # 检查页面上的状态
                try:
                    status_text = page.inner_text('body')
                    if 'Ready' in status_text or 'Deployed' in status_text or 'Building' not in status_text:
                        print("[OK] 部署似乎已完成或正在进行中")
                        if waited >= 60:  # 至少等待1分钟
                            break
                except:
                    pass
            
            # 步骤 7: 验证 API
            print_step("验证 API 是否正常工作")
            page.goto(API_CHECK_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            # 获取页面内容并解析 JSON
            try:
                # 使用 evaluate 获取 JSON
                data = page.evaluate("""
                    async () => {
                        try {
                            const response = await fetch(window.location.href);
                            return await response.json();
                        } catch (e) {
                            return { error: e.message };
                        }
                    }
                """)
                
                if 'error' in data:
                    # 如果 fetch 失败，尝试从页面文本解析
                    content = page.inner_text('body')
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                    else:
                        raise Exception("无法解析 JSON")
                else:
                    print(f"[OK] API 响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except Exception as e:
                print(f"[WARN] 解析 API 响应时出错: {e}")
                print("尝试从页面内容提取...")
                content = page.content()
                if '<pre>' in content:
                    import re
                    json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        data = json.loads(json_str)
                    else:
                        print("[ERROR] 无法解析 API 响应")
                        data = {}
                else:
                    data = {}
            
            total_intents = data.get('data', {}).get('total_intents', 0)
            
            if total_intents == 0:
                print("\n" + "="*60)
                print("[WARN] total_intents 仍为 0")
                print("请检查 Supabase 表名是否为小写的 purchases")
                print("="*60 + "\n")
            else:
                print("\n" + "="*60)
                print(f"[SUCCESS] total_intents = {total_intents}")
                print("环境变量配置成功，API 正常工作！")
                print("="*60 + "\n")
            
            print_step("配置完成！")
            print("浏览器将保持打开 10 秒，然后自动关闭...")
            page.wait_for_timeout(10000)
            
            try:
                context.close()
            except:
                try:
                    browser.close()
                except:
                    pass
            
        except Exception as e:
            error_msg = str(e).encode('ascii', 'ignore').decode('ascii')  # 移除非ASCII字符
            print(f"\n[ERROR] 发生错误: {error_msg}")
            print("可能原因：Chrome 浏览器正在运行，请关闭所有 Chrome 窗口后重试")
            print("浏览器将保持打开，请手动检查...")
            try:
                import traceback
                traceback.print_exc()
            except:
                pass
            try:
                page.wait_for_timeout(30000)  # 保持打开30秒以便调试
            except:
                pass

if __name__ == "__main__":
    main()
