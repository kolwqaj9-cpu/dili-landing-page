#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控脚本：检查 Vercel API 是否成功连接 Supabase
每隔 3 秒请求一次，直到 total_intents 变成 1
"""

import time
import requests
import json
from datetime import datetime

API_URL = "https://baseprops.vercel.app/api/stats/purchases"
MAX_FAILED_ATTEMPTS = 10  # 连续失败次数阈值

def print_success(msg):
    """打印成功消息"""
    print(f"\033[92m{msg}\033[0m")

def print_error(msg):
    """打印错误消息"""
    print(f"\033[91m{msg}\033[0m")

def print_info(msg):
    """打印信息消息"""
    print(f"\033[94m{msg}\033[0m")

def print_warning(msg):
    """打印警告消息"""
    print(f"\033[93m{msg}\033[0m")

def analyze_error(response_data, status_code):
    """分析错误信息"""
    print_error("=" * 60)
    print_error("错误分析：")
    print_error("=" * 60)
    
    if status_code != 200:
        print_error(f"HTTP 状态码: {status_code}")
        print_error("可能原因：")
        print_error("  1. Vercel 服务未部署或部署失败")
        print_error("  2. API 路由配置错误")
        print_error("  3. 服务器内部错误")
    
    if isinstance(response_data, dict):
        if response_data.get('status') == 'error':
            error_msg = response_data.get('message', response_data.get('msg', 'Unknown error'))
            print_error(f"API 错误信息: {error_msg}")
            print_error("\n可能原因：")
            
            if 'connection' in error_msg.lower() or 'connect' in error_msg.lower():
                print_error("  1. Supabase 连接失败")
                print_error("  2. 检查 SUPABASE_URL 环境变量是否正确")
            elif 'table' in error_msg.lower() or 'relation' in error_msg.lower():
                print_error("  1. 数据库表不存在或表名错误")
                print_error("  2. 检查表名是否为小写的 'purchases'")
                print_error("  3. 检查 Supabase 中是否已创建 purchases 表")
            elif 'key' in error_msg.lower() or 'auth' in error_msg.lower():
                print_error("  1. Supabase 密钥错误或权限不足")
                print_error("  2. 检查 SUPABASE_SERVICE_ROLE_KEY 环境变量")
                print_error("  3. 确认使用的是 Service Role Key（不是 anon key）")
            elif 'timeout' in error_msg.lower():
                print_error("  1. 数据库查询超时")
                print_error("  2. Supabase 服务可能暂时不可用")
            else:
                print_error(f"  未知错误: {error_msg}")
        
        print_error(f"\n完整响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
    else:
        print_error(f"响应不是 JSON 格式: {response_data}")
    
    print_error("=" * 60)

def main():
    print_info("=" * 60)
    print_info("开始监控 API 状态...")
    print_info(f"API URL: {API_URL}")
    print_info(f"检查间隔: 3 秒")
    print_info(f"最大失败次数: {MAX_FAILED_ATTEMPTS}")
    print_info("=" * 60)
    print()
    
    failed_count = 0
    attempt = 0
    
    try:
        while True:
            attempt += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            try:
                print_info(f"[{timestamp}] 第 {attempt} 次检查...")
                response = requests.get(API_URL, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('status') == 'success':
                        result_data = data.get('data', {})
                        total_intents = result_data.get('total_intents', 0)
                        total_revenue = result_data.get('total_revenue', 0)
                        recent_count = len(result_data.get('recent_purchases', []))
                        
                        print_info(f"  total_intents: {total_intents}")
                        print_info(f"  total_revenue: ${total_revenue}")
                        print_info(f"  recent_purchases: {recent_count} 条")
                        
                        if total_intents >= 1:
                            print_success("=" * 60)
                            print_success("🎉 成功打通！")
                            print_success("=" * 60)
                            print_success(f"总订单数: {total_intents}")
                            print_success(f"总收入: ${total_revenue}")
                            print_success("API 已成功连接到 Supabase 数据库！")
                            print_success("=" * 60)
                            break
                        else:
                            failed_count += 1
                            print_warning(f"  total_intents 仍为 0 (连续检查: {failed_count}/{MAX_FAILED_ATTEMPTS})")
                            
                            if failed_count >= MAX_FAILED_ATTEMPTS:
                                print_warning("\n" + "=" * 60)
                                print_warning(f"连续 {MAX_FAILED_ATTEMPTS} 次检查，total_intents 仍为 0")
                                print_warning("=" * 60)
                                print_info("\n分析结果：")
                                print_info("  API 连接正常（返回 status: success）")
                                print_info("  Supabase 连接正常（无错误信息）")
                                print_warning("\n可能原因：")
                                print_warning("  1. 数据库中确实没有 status='paid' 的记录")
                                print_warning("  2. 需要先通过 checkout.html 创建购买记录")
                                print_warning("  3. 或者检查数据库中是否有其他状态的记录")
                                print_info(f"\n完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                                print_warning("=" * 60)
                                break
                    else:
                        failed_count += 1
                        print_error(f"  API 返回错误状态: {data.get('status')}")
                        if failed_count >= MAX_FAILED_ATTEMPTS:
                            analyze_error(data, response.status_code)
                            break
                else:
                    failed_count += 1
                    print_error(f"  HTTP 状态码: {response.status_code}")
                    try:
                        error_data = response.json()
                        if failed_count >= MAX_FAILED_ATTEMPTS:
                            analyze_error(error_data, response.status_code)
                            break
                    except:
                        if failed_count >= MAX_FAILED_ATTEMPTS:
                            analyze_error(response.text, response.status_code)
                            break
                
            except requests.exceptions.Timeout:
                failed_count += 1
                print_error(f"  请求超时（超过 10 秒）")
                if failed_count >= MAX_FAILED_ATTEMPTS:
                    print_error("\n连续超时，可能原因：")
                    print_error("  1. Vercel 服务未响应")
                    print_error("  2. 网络连接问题")
                    break
            except requests.exceptions.RequestException as e:
                failed_count += 1
                print_error(f"  请求失败: {str(e)}")
                if failed_count >= MAX_FAILED_ATTEMPTS:
                    print_error("\n连续请求失败，可能原因：")
                    print_error("  1. API 地址错误")
                    print_error("  2. Vercel 服务未部署")
                    print_error("  3. 网络连接问题")
                    break
            except Exception as e:
                failed_count += 1
                print_error(f"  发生未知错误: {str(e)}")
                if failed_count >= MAX_FAILED_ATTEMPTS:
                    analyze_error({"error": str(e)}, 0)
                    break
            
            if failed_count < MAX_FAILED_ATTEMPTS:
                print_info(f"  等待 3 秒后继续...")
                print()
                time.sleep(3)
            else:
                break
        
        if failed_count >= MAX_FAILED_ATTEMPTS:
            print_error("\n监控已停止（达到最大失败次数）")
        else:
            print_info("\n监控已停止（检测到成功）")
            
    except KeyboardInterrupt:
        print_warning("\n\n监控被用户中断")
        print_info("已停止监控")

if __name__ == "__main__":
    main()
