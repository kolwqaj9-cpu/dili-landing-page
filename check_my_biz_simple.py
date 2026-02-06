#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版自动化测试脚本：验证后端 API 数据
使用 requests 库（无需浏览器）
"""

import json
import sys

try:
    import requests
except ImportError:
    print("❌ 错误: 需要安装 requests 库")
    print("请运行: pip install requests")
    sys.exit(1)

# ==================== 配置区域 ====================
API_URL = "https://baseprops.vercel.app/api/stats/purchases"
EXPECTED_PROJECT_ID = "bmwfnuekfgolwutnffmf"
FRONTEND_URL = "https://baseprops.tech/purchase_stats.html"
# =================================================

def print_success(msg):
    """打印成功消息（绿色）"""
    print(f"\033[92m[OK] {msg}\033[0m")

def print_error(msg):
    """打印错误消息（红色）"""
    print(f"\033[91m[ERROR] {msg}\033[0m")

def print_warning(msg):
    """打印警告消息（黄色）"""
    print(f"\033[93m[WARN] {msg}\033[0m")

def print_info(msg):
    """打印信息消息（蓝色）"""
    print(f"\033[94m[INFO] {msg}\033[0m")

def fetch_api_data():
    """动作 A：直接访问 API_URL，读取返回的 JSON 响应"""
    print_info(f"正在访问 API: {API_URL}")
    
    try:
        response = requests.get(API_URL, timeout=10)
        
        if response.status_code != 200:
            print_error(f"API 返回状态码: {response.status_code}")
            return None
        
        data = response.json()
        return data
        
    except requests.exceptions.Timeout:
        print_error("请求超时（超过 10 秒）")
        print_warning("请检查 Vercel 服务是否在线")
        return None
    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {str(e)}")
        print_warning("请检查网络连接和 Vercel 服务状态")
        return None
    except json.JSONDecodeError:
        print_error("API 返回的不是有效的 JSON 格式")
        print_info(f"响应内容: {response.text[:200]}")
        return None

def check_api_data(data):
    """动作 B 和 C：检查 API 返回的数据"""
    if not data:
        return False, 0
    
    print_info(f"API 响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # 检查响应结构
    if data.get('status') != 'success':
        print_error(f"API 返回状态: {data.get('status', 'unknown')}")
        print_error(f"错误信息: {data.get('msg', 'No message')}")
        return False, 0
    
    data_obj = data.get('data', {})
    total_intents = data_obj.get('total_intents', 0)
    
    # 动作 B：如果 total_intents 为 0
    if total_intents == 0:
        print_error("=" * 60)
        print_error("API 连接成功但未读到数据")
        print_error("请检查 Vercel 的环境变量是否已 Redeploy 且钥匙正确")
        print_error("=" * 60)
        return False, 0
    
    # 动作 C：如果 total_intents >= 1
    if total_intents >= 1:
        print_success("=" * 60)
        print_success("恭喜！云端大脑已通，数据库数据已成功拉取")
        print_success(f"总购买意向数: {total_intents}")
        print_success(f"预估收入: ${total_intents * 99:,}")
        print_success("=" * 60)
        return True, total_intents
    
    return False, 0

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
    api_success, api_total = check_api_data(api_data)
    
    if not api_success:
        print_warning("API 数据检查未通过")
        sys.exit(1)
    
    print()
    print_info("=" * 60)
    print_success("API 测试通过！")
    print_info("=" * 60)
    print()
    print_info("提示: 前端页面对比需要使用浏览器，请手动访问:")
    print_info(f"  {FRONTEND_URL}")
    print_info("  检查页面显示的数字是否与 API 数据一致")

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
