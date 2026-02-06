#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试脚本：验证后端 API 和前端页面数据一致性
使用 Playwright 进行浏览器自动化测试
"""

import json
import sys
from playwright.sync_api import sync_playwright
from colorama import init, Fore, Style

# 初始化 colorama（用于终端颜色输出）
init(autoreset=True)

# ==================== 配置区域 ====================
API_URL = "https://baseprops.vercel.app/api/stats/purchases"
EXPECTED_PROJECT_ID = "bmwfnuekfgolwutnffmf"
FRONTEND_URL = "https://baseprops.tech/purchase_stats.html"
# =================================================

def print_success(msg):
    """打印成功消息（绿色）"""
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

def print_error(msg):
    """打印错误消息（红色）"""
    print(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")

def print_warning(msg):
    """打印警告消息（黄色）"""
    print(f"{Fore.YELLOW}⚠️  {msg}{Style.RESET_ALL}")

def print_info(msg):
    """打印信息消息（蓝色）"""
    print(f"{Fore.CYAN}ℹ️  {msg}{Style.RESET_ALL}")

def fetch_api_data():
    """动作 A：直接访问 API_URL，读取返回的 JSON 响应"""
    print_info(f"正在访问 API: {API_URL}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # 设置超时时间为 10 秒
            page.set_default_timeout(10000)
            
            # 访问 API URL
            response = page.goto(API_URL, wait_until="networkidle")
            
            if response.status != 200:
                print_error(f"API 返回状态码: {response.status}")
                browser.close()
                return None
            
            # 获取响应内容
            content = page.content()
            browser.close()
            
            # 尝试解析 JSON（可能在 <pre> 标签中）
            try:
                # 如果返回的是 HTML，尝试提取 JSON
                if '<pre>' in content:
                    import re
                    json_match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        data = json.loads(json_str)
                    else:
                        # 尝试直接解析整个 body
                        data = json.loads(content)
                else:
                    data = json.loads(content)
            except json.JSONDecodeError:
                # 如果直接访问返回 HTML，使用 fetch API
                print_info("API 返回 HTML，尝试使用 fetch API...")
                with sync_playwright() as p2:
                    browser2 = p2.chromium.launch(headless=True)
                    context2 = browser2.new_context()
                    page2 = context2.new_page()
                    
                    # 使用 evaluate 执行 fetch
                    result = page2.evaluate(f"""
                        async () => {{
                            try {{
                                const response = await fetch('{API_URL}');
                                return await response.json();
                            }} catch (e) {{
                                return {{ error: e.message }};
                            }}
                        }}
                    """)
                    browser2.close()
                    
                    if 'error' in result:
                        raise Exception(result['error'])
                    data = result
            
            return data
            
    except Exception as e:
        print_error(f"请求超时或失败: {str(e)}")
        print_warning("请检查 Vercel 服务是否在线")
        return None

def check_api_data(data):
    """动作 B 和 C：检查 API 返回的数据"""
    if not data:
        return False
    
    print_info(f"API 响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # 检查响应结构
    if data.get('status') != 'success':
        print_error(f"API 返回状态: {data.get('status', 'unknown')}")
        print_error(f"错误信息: {data.get('msg', 'No message')}")
        return False
    
    data_obj = data.get('data', {})
    total_intents = data_obj.get('total_intents', 0)
    
    # 动作 B：如果 total_intents 为 0
    if total_intents == 0:
        print_error("=" * 60)
        print_error("API 连接成功但未读到数据")
        print_error("请检查 Vercel 的环境变量是否已 Redeploy 且钥匙正确")
        print_error("=" * 60)
        return False
    
    # 动作 C：如果 total_intents >= 1
    if total_intents >= 1:
        print_success("=" * 60)
        print_success("恭喜！云端大脑已通，数据库数据已成功拉取")
        print_success(f"总购买意向数: {total_intents}")
        print_success(f"预估收入: ${total_intents * 99:,}")
        print_success("=" * 60)
        return True
    
    return False

def check_frontend_data(api_total):
    """动作 D：访问前端页面，对比网页上显示的数字是否与 API 一致"""
    print_info(f"正在访问前端页面: {FRONTEND_URL}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # 设置超时
            page.set_default_timeout(15000)
            
            # 访问前端页面
            page.goto(FRONTEND_URL, wait_until="networkidle")
            
            # 等待页面加载完成
            page.wait_for_timeout(2000)
            
            # 提取页面上的统计数字
            try:
                # 等待元素出现
                page.wait_for_selector('#count', timeout=5000)
                
                # 获取页面显示的总数
                frontend_count_text = page.inner_text('#count')
                
                # 清理文本（移除可能的 "Loading..." 等）
                frontend_count = None
                if frontend_count_text and frontend_count_text.isdigit():
                    frontend_count = int(frontend_count_text)
                elif frontend_count_text and frontend_count_text.replace(',', '').isdigit():
                    frontend_count = int(frontend_count_text.replace(',', ''))
                
                browser.close()
                
                if frontend_count is None:
                    print_warning("无法从页面提取数字，可能页面还在加载")
                    return False
                
                print_info(f"前端页面显示的总数: {frontend_count}")
                print_info(f"API 返回的总数: {api_total}")
                
                # 对比数据
                if frontend_count == api_total:
                    print_success("=" * 60)
                    print_success("数据一致性验证通过！")
                    print_success(f"前端显示 ({frontend_count}) = API 数据 ({api_total})")
                    print_success("=" * 60)
                    return True
                else:
                    print_warning("=" * 60)
                    print_warning("数据不一致！")
                    print_warning(f"前端显示: {frontend_count}")
                    print_warning(f"API 数据: {api_total}")
                    print_warning("可能原因：前端使用了 localStorage 后备数据")
                    print_warning("=" * 60)
                    return False
                    
            except Exception as e:
                browser.close()
                print_error(f"无法提取页面数据: {str(e)}")
                return False
                
    except Exception as e:
        print_error(f"访问前端页面失败: {str(e)}")
        return False

def main():
    """主函数"""
    print_info("=" * 60)
    print_info("开始自动化测试...")
    print_info(f"API URL: {API_URL}")
    print_info(f"预期项目 ID: {EXPECTED_PROJECT_ID}")
    print_info("=" * 60)
    print()
    
    # 动作 A：获取 API 数据
    api_data = fetch_api_data()
    
    if not api_data:
        print_error("无法获取 API 数据，测试终止")
        sys.exit(1)
    
    # 动作 B 和 C：检查 API 数据
    api_total = api_data.get('data', {}).get('total_intents', 0)
    api_success = check_api_data(api_data)
    
    if not api_success:
        print_warning("API 数据检查未通过，跳过前端对比")
        sys.exit(1)
    
    print()
    
    # 动作 D：检查前端数据
    frontend_match = check_frontend_data(api_total)
    
    print()
    print_info("=" * 60)
    if frontend_match:
        print_success("所有测试通过！")
    else:
        print_warning("测试完成，但前端数据与 API 不一致")
    print_info("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
