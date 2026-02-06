"""
全面诊断连接错误问题
检查所有可能导致 "Connection error" 的原因
"""

import os
import sys
import json
import requests
import subprocess
import socket
from pathlib import Path

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "[OK]" if exists else "[FAIL]"
    print(f"  {status} {description}: {filepath}")
    if not exists:
        print(f"    → 文件不存在，这会导致问题！")
    return exists

def check_process_running(process_name):
    """检查进程是否运行"""
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
        
        status = "[OK]" if is_running else "[FAIL]"
        print(f"  {status} {process_name} 进程: {'运行中' if is_running else '未运行'}")
        return is_running
    except Exception as e:
        print(f"  [WARN] 无法检查进程: {e}")
        return False

def check_port_listening(port, description):
    """检查端口是否在监听"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        is_listening = result == 0
        status = "[OK]" if is_listening else "[FAIL]"
        print(f"  {status} {description} (端口 {port}): {'正在监听' if is_listening else '未监听'}")
        return is_listening
    except Exception as e:
        print(f"  [WARN] 无法检查端口: {e}")
        return False

def check_api_endpoint(url, method="GET", data=None):
    """检查 API 端点是否可访问"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5, headers={'Content-Type': 'application/json'})
        
        status_code = response.status_code
        if status_code < 500:
            print(f"  [OK] API 端点可访问: {url}")
            print(f"      状态码: {status_code}")
            if status_code == 405:
                print(f"      → 这是正常的（GET 方法不允许，需要 POST）")
            return True
        else:
            print(f"  [FAIL] API 端点错误: {url}")
            print(f"      状态码: {status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  [FAIL] API 端点无法连接: {url}")
        print(f"      → 可能原因: Cloudflared 隧道未运行，或后端服务未运行")
        return False
    except requests.exceptions.Timeout:
        print(f"  [FAIL] API 端点超时: {url}")
        return False
    except Exception as e:
        print(f"  [FAIL] API 端点检查失败: {e}")
        return False

def verify_landing_html():
    """验证 landing.html 中的 API 配置"""
    print_section("检查 1: Landing 页面 API 配置")
    
    landing_file = "landing.html"
    if not os.path.exists(landing_file):
        print(f"  [FAIL] {landing_file} 不存在")
        return False
    
    try:
        with open(landing_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查 API_WEBHOOK 定义
        if "API_WEBHOOK" in content:
            print("  [OK] 找到 API_WEBHOOK 定义")
            
            # 提取 API URL
            import re
            match = re.search(r"const API_WEBHOOK = ['\"]([^'\"]+)['\"]", content)
            if match:
                api_url = match.group(1)
                print(f"  [OK] API URL: {api_url}")
                
                if api_url == "https://api.propkitai.tech/api/webhook":
                    print("  [OK] API URL 配置正确")
                    return True
                else:
                    print(f"  [WARN] API URL 可能不正确: {api_url}")
                    print(f"      期望: https://api.propkitai.tech/api/webhook")
                    return False
            else:
                print("  [FAIL] 无法提取 API URL")
                return False
        else:
            print("  [FAIL] 未找到 API_WEBHOOK 定义")
            return False
        
        # 检查 activateTrial 函数
        if "activateTrial" in content:
            print("  [OK] 找到 activateTrial 函数")
        else:
            print("  [FAIL] 未找到 activateTrial 函数")
            return False
        
        # 检查 fetch 调用
        if "fetch(API_WEBHOOK" in content:
            print("  [OK] 找到 fetch API 调用")
        else:
            print("  [FAIL] 未找到 fetch API 调用")
            return False
            
    except Exception as e:
        print(f"  [FAIL] 读取文件失败: {e}")
        return False

def verify_backend_code():
    """验证后端代码配置"""
    print_section("检查 2: 后端代码配置")
    
    main_file = "main.py"
    if not check_file_exists(main_file, "后端主文件"):
        return False
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查 FastAPI 应用
        if "FastAPI" in content:
            print("  [OK] 使用 FastAPI 框架")
        else:
            print("  [FAIL] 未找到 FastAPI")
            return False
        
        # 检查 CORS 配置
        if "CORSMiddleware" in content:
            print("  [OK] CORS 中间件已配置")
        else:
            print("  [WARN] 未找到 CORS 配置，可能导致跨域问题")
        
        # 检查 webhook 端点
        if "@app.post(\"/api/webhook\")" in content or '@app.post("/api/webhook")' in content:
            print("  [OK] Webhook 端点已定义: /api/webhook")
        else:
            print("  [FAIL] 未找到 /api/webhook 端点")
            return False
        
        # 检查端口配置
        if "port=8000" in content or "port = 8000" in content:
            print("  [OK] 端口配置: 8000")
        else:
            print("  [WARN] 未找到端口 8000 配置")
        
        return True
    except Exception as e:
        print(f"  [FAIL] 读取文件失败: {e}")
        return False

def verify_cloudflare_config():
    """验证 Cloudflare 隧道配置"""
    print_section("检查 3: Cloudflare 隧道配置")
    
    config_file = "config.yml"
    if not check_file_exists(config_file, "Cloudflare 配置文件"):
        return False
    
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查 ingress 配置
        if 'ingress' in config:
            ingress = config['ingress']
            print(f"  [OK] 找到 ingress 配置")
            
            # 查找 api.propkitai.tech 的映射
            found = False
            for rule in ingress:
                if isinstance(rule, dict) and rule.get('hostname') == 'api.propkitai.tech':
                    service = rule.get('service', '')
                    print(f"  [OK] 找到域名映射: api.propkitai.tech → {service}")
                    if service == "http://localhost:8000":
                        print("  [OK] 服务地址配置正确")
                        found = True
                    else:
                        print(f"  [WARN] 服务地址可能不正确: {service}")
                        print(f"      期望: http://localhost:8000")
            
            if not found:
                print("  [FAIL] 未找到 api.propkitai.tech 的映射配置")
                return False
        else:
            print("  [FAIL] 未找到 ingress 配置")
            return False
        
        return True
    except ImportError:
        print("  [WARN] PyYAML 未安装，跳过详细检查")
        # 简单文本检查
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'api.propkitai.tech' in content and 'localhost:8000' in content:
                print("  [OK] 配置文件包含正确的域名和服务地址")
                return True
            else:
                print("  [FAIL] 配置文件可能不正确")
                return False
    except Exception as e:
        print(f"  [FAIL] 读取配置文件失败: {e}")
        return False

def check_runtime_services():
    """检查运行时服务"""
    print_section("检查 4: 运行时服务状态")
    
    # 检查 Cloudflared
    cloudflared_ok = check_process_running("cloudflared")
    
    # 检查 Python 后端
    python_ok = check_process_running("python")
    
    # 检查端口 8000
    port_ok = check_port_listening(8000, "Python 后端服务")
    
    return cloudflared_ok, python_ok, port_ok

def check_api_connectivity():
    """检查 API 连接性"""
    print_section("检查 5: API 连接性测试")
    
    api_url = "https://api.propkitai.tech/api/webhook"
    
    # 测试 GET（应该返回 405 Method Not Allowed，说明端点存在）
    print("\n  测试 1: GET 请求（应该返回 405）...")
    get_ok = check_api_endpoint(api_url, method="GET")
    
    # 测试 POST（应该返回 200 或 422）
    print("\n  测试 2: POST 请求（正确方法）...")
    post_ok = check_api_endpoint(api_url, method="POST", data={"email": "test@example.com"})
    
    return get_ok or post_ok  # 只要有一个能连接就说明服务可达

def check_local_backend():
    """检查本地后端"""
    print_section("检查 6: 本地后端服务")
    
    local_url = "http://127.0.0.1:8000/api/webhook"
    
    print("\n  测试本地后端 (http://127.0.0.1:8000/api/webhook)...")
    local_ok = check_api_endpoint(local_url, method="POST", data={"email": "test@example.com"})
    
    return local_ok

def main():
    print("\n" + "=" * 60)
    print("  连接错误全面诊断")
    print("=" * 60)
    print("\n检查所有可能导致 'Connection error' 的原因...")
    
    results = {
        'landing_config': False,
        'backend_config': False,
        'cloudflare_config': False,
        'services_running': False,
        'api_accessible': False,
        'local_backend': False
    }
    
    # 检查 1: Landing 页面配置
    results['landing_config'] = verify_landing_html()
    
    # 检查 2: 后端代码配置
    results['backend_config'] = verify_backend_code()
    
    # 检查 3: Cloudflare 配置
    results['cloudflare_config'] = verify_cloudflare_config()
    
    # 检查 4: 运行时服务
    cloudflared_ok, python_ok, port_ok = check_runtime_services()
    results['services_running'] = cloudflared_ok and python_ok and port_ok
    
    # 检查 5: API 连接性
    results['api_accessible'] = check_api_connectivity()
    
    # 检查 6: 本地后端
    results['local_backend'] = check_local_backend()
    
    # 总结
    print_section("诊断总结")
    
    all_checks = [
        ("Landing 页面配置", results['landing_config']),
        ("后端代码配置", results['backend_config']),
        ("Cloudflare 配置", results['cloudflare_config']),
        ("运行时服务", results['services_running']),
        ("API 可访问性", results['api_accessible']),
        ("本地后端", results['local_backend'])
    ]
    
    passed = sum(1 for _, ok in all_checks if ok)
    total = len(all_checks)
    
    print(f"\n检查结果: {passed}/{total} 通过\n")
    
    for name, ok in all_checks:
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {name}")
    
    # 问题诊断和建议
    print_section("问题诊断和建议")
    
    if not results['landing_config']:
        print("\n  [FAIL] Landing 页面配置有问题")
        print("     -> 检查 landing.html 中的 API_WEBHOOK 配置")
    
    if not results['backend_config']:
        print("\n  [FAIL] 后端代码配置有问题")
        print("     -> 检查 main.py 中的端点定义")
    
    if not results['cloudflare_config']:
        print("\n  [FAIL] Cloudflare 配置有问题")
        print("     -> 检查 config.yml 中的域名映射")
    
    if not results['services_running']:
        print("\n  [FAIL] 运行时服务未运行")
        print("     -> 运行 start_services.ps1 启动服务")
        print("     -> 或运行: .\\一键启动.bat")
    
    if not results['api_accessible']:
        print("\n  [FAIL] API 无法访问")
        if not results['services_running']:
            print("     -> 首先启动服务（见上）")
        else:
            print("     -> 检查 Cloudflare 隧道是否正常连接")
            print("     -> 检查域名 DNS 配置")
    
    if not results['local_backend']:
        print("\n  [FAIL] 本地后端无法访问")
        print("     -> 检查 Python 后端是否在运行")
        print("     -> 检查端口 8000 是否被占用")
    
    # 如果所有配置都正确但服务未运行
    if (results['landing_config'] and results['backend_config'] and 
        results['cloudflare_config'] and not results['services_running']):
        print("\n" + "=" * 60)
        print("  ✅ 配置检查通过，但服务未运行")
        print("=" * 60)
        print("\n  解决方案:")
        print("  1. 运行启动脚本:")
        print("     .\\start_services.ps1")
        print("     或")
        print("     .\\一键启动.bat")
        print("\n  2. 等待 10-15 秒让服务启动")
        print("\n  3. 再次运行此诊断脚本验证")
    
    # 如果所有检查都通过
    if all(results.values()):
        print("\n" + "=" * 60)
        print("  ✅ 所有检查通过！")
        print("=" * 60)
        print("\n  如果仍然出现连接错误，可能是:")
        print("  1. 浏览器缓存问题（尝试 Ctrl+F5 或无痕窗口）")
        print("  2. 网络连接问题")
        print("  3. Cloudflare 隧道临时故障（等待几分钟后重试）")
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] 诊断被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
