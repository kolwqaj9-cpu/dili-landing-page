"""
全面诊断 - 检查所有可能的错误点
"""

import os
import sys
import json
import requests
import subprocess
import socket
import re

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_1_landing_html_code():
    """检查 1: landing.html 代码逻辑"""
    print_section("检查 1: landing.html 代码逻辑")
    
    issues = []
    
    if not os.path.exists("landing.html"):
        print("  [FAIL] landing.html 文件不存在")
        return False, ["文件不存在"]
    
    with open("landing.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查 API_WEBHOOK 定义
    api_match = re.search(r"const API_WEBHOOK\s*=\s*['\"]([^'\"]+)['\"]", content)
    if not api_match:
        issues.append("未找到 API_WEBHOOK 定义")
        print("  [FAIL] 未找到 API_WEBHOOK 定义")
    else:
        api_url = api_match.group(1)
        print(f"  [OK] API_WEBHOOK = {api_url}")
        
        if api_url != "https://api.propkitai.tech/api/webhook":
            issues.append(f"API URL 不正确: {api_url}")
            print(f"  [FAIL] API URL 不正确: {api_url}")
            print(f"         期望: https://api.propkitai.tech/api/webhook")
    
    # 检查 fetch 调用
    if "fetch(API_WEBHOOK" not in content:
        issues.append("未找到 fetch(API_WEBHOOK) 调用")
        print("  [FAIL] 未找到 fetch API 调用")
    else:
        print("  [OK] 找到 fetch API 调用")
        
        # 检查 fetch 参数
        fetch_match = re.search(r"fetch\(API_WEBHOOK[^)]+\)", content, re.DOTALL)
        if fetch_match:
            fetch_code = fetch_match.group(0)
            if "method: 'POST'" not in fetch_code and 'method: "POST"' not in fetch_code:
                issues.append("fetch 未使用 POST 方法")
                print("  [FAIL] fetch 未使用 POST 方法")
            else:
                print("  [OK] fetch 使用 POST 方法")
            
            if "Content-Type" not in fetch_code:
                issues.append("fetch 缺少 Content-Type header")
                print("  [FAIL] fetch 缺少 Content-Type header")
            else:
                print("  [OK] fetch 包含 Content-Type header")
            
            if "JSON.stringify" not in fetch_code:
                issues.append("fetch 未使用 JSON.stringify")
                print("  [FAIL] fetch 未使用 JSON.stringify")
            else:
                print("  [OK] fetch 使用 JSON.stringify")
    
    # 检查错误处理
    if "catch (error)" not in content:
        issues.append("缺少错误处理")
        print("  [FAIL] 缺少错误处理")
    else:
        print("  [OK] 有错误处理")
    
    return len(issues) == 0, issues

def check_2_backend_code():
    """检查 2: 后端代码"""
    print_section("检查 2: 后端代码 (main.py)")
    
    issues = []
    
    if not os.path.exists("main.py"):
        print("  [FAIL] main.py 文件不存在")
        return False, ["文件不存在"]
    
    with open("main.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查 FastAPI
    if "FastAPI()" not in content:
        issues.append("未找到 FastAPI 应用")
        print("  [FAIL] 未找到 FastAPI 应用")
    else:
        print("  [OK] FastAPI 应用存在")
    
    # 检查 CORS
    if "CORSMiddleware" not in content:
        issues.append("未找到 CORS 中间件")
        print("  [FAIL] 未找到 CORS 中间件")
    else:
        print("  [OK] CORS 中间件存在")
        if "allow_origins" in content and '"*"' in content:
            print("  [OK] CORS 允许所有来源")
        else:
            issues.append("CORS 可能未允许所有来源")
            print("  [WARN] CORS 配置可能有问题")
    
    # 检查端点
    if '@app.post("/api/webhook")' not in content and '@app.post(\"/api/webhook\")' not in content:
        issues.append("未找到 /api/webhook 端点")
        print("  [FAIL] 未找到 /api/webhook 端点")
    else:
        print("  [OK] /api/webhook 端点存在")
    
    # 检查端口
    if "port=8000" not in content and "port = 8000" not in content:
        issues.append("未找到端口 8000 配置")
        print("  [FAIL] 未找到端口 8000 配置")
    else:
        print("  [OK] 端口 8000 配置存在")
    
    # 检查 host
    if "host=" in content:
        host_match = re.search(r"host\s*=\s*['\"]([^'\"]+)['\"]", content)
        if host_match:
            host = host_match.group(1)
            if host not in ["127.0.0.1", "localhost", "0.0.0.0"]:
                issues.append(f"Host 配置可能有问题: {host}")
                print(f"  [WARN] Host: {host}")
            else:
                print(f"  [OK] Host: {host}")
    
    return len(issues) == 0, issues

def check_3_cloudflare_config():
    """检查 3: Cloudflare 配置"""
    print_section("检查 3: Cloudflare 隧道配置 (config.yml)")
    
    issues = []
    
    if not os.path.exists("config.yml"):
        print("  [FAIL] config.yml 文件不存在")
        return False, ["文件不存在"]
    
    with open("config.yml", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查域名映射
    if "api.propkitai.tech" not in content:
        issues.append("未找到 api.propkitai.tech 配置")
        print("  [FAIL] 未找到 api.propkitai.tech")
    else:
        print("  [OK] 找到 api.propkitai.tech")
    
    if "localhost:8000" not in content:
        issues.append("未找到 localhost:8000 映射")
        print("  [FAIL] 未找到 localhost:8000 映射")
    else:
        print("  [OK] 找到 localhost:8000 映射")
        
        # 检查映射关系
        lines = content.split('\n')
        in_ingress = False
        found_mapping = False
        for i, line in enumerate(lines):
            if 'ingress:' in line:
                in_ingress = True
            elif in_ingress and 'api.propkitai.tech' in line:
                # 检查下一行是否是 service
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if 'localhost:8000' in next_line:
                        found_mapping = True
                        print("  [OK] 域名映射关系正确")
        
        if not found_mapping:
            issues.append("域名映射关系可能不正确")
            print("  [WARN] 域名映射关系可能不正确")
    
    return len(issues) == 0, issues

def check_4_runtime_services():
    """检查 4: 运行时服务"""
    print_section("检查 4: 运行时服务状态")
    
    issues = []
    
    # 检查 Cloudflared
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq cloudflared.exe"],
            capture_output=True,
            text=True,
            timeout=5
        )
        cloudflared_running = "cloudflared.exe" in result.stdout
        if cloudflared_running:
            print("  [OK] Cloudflared 进程运行中")
        else:
            issues.append("Cloudflared 未运行")
            print("  [FAIL] Cloudflared 进程未运行")
    except Exception as e:
        issues.append(f"无法检查 Cloudflared: {e}")
        print(f"  [WARN] 无法检查 Cloudflared: {e}")
    
    # 检查 Python 后端
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe"],
            capture_output=True,
            text=True,
            timeout=5
        )
        python_running = "python.exe" in result.stdout
        if python_running:
            print("  [OK] Python 进程运行中")
        else:
            issues.append("Python 后端未运行")
            print("  [FAIL] Python 后端进程未运行")
    except Exception as e:
        issues.append(f"无法检查 Python: {e}")
        print(f"  [WARN] 无法检查 Python: {e}")
    
    # 检查端口 8000
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        if result == 0:
            print("  [OK] 端口 8000 正在监听")
        else:
            issues.append("端口 8000 未监听")
            print("  [FAIL] 端口 8000 未监听")
    except Exception as e:
        issues.append(f"无法检查端口: {e}")
        print(f"  [WARN] 无法检查端口: {e}")
    
    return len(issues) == 0, issues

def check_5_api_connectivity():
    """检查 5: API 连接性"""
    print_section("检查 5: API 连接性测试")
    
    issues = []
    
    # 测试本地后端
    print("\n  测试 5.1: 本地后端 (http://127.0.0.1:8000/api/webhook)")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/webhook",
            json={"email": "test@example.com"},
            headers={"Content-Type": "application/json"},
            timeout=3
        )
        print(f"  [OK] 本地后端可访问 (状态码: {response.status_code})")
    except requests.exceptions.ConnectionError:
        issues.append("本地后端无法连接")
        print("  [FAIL] 本地后端无法连接 (服务可能未运行)")
    except requests.exceptions.Timeout:
        issues.append("本地后端超时")
        print("  [FAIL] 本地后端超时")
    except Exception as e:
        issues.append(f"本地后端测试失败: {e}")
        print(f"  [FAIL] 本地后端测试失败: {e}")
    
    # 测试 Cloudflare 隧道
    print("\n  测试 5.2: Cloudflare 隧道 (https://api.propkitai.tech/api/webhook)")
    try:
        response = requests.post(
            "https://api.propkitai.tech/api/webhook",
            json={"email": "test@example.com"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"  [OK] Cloudflare 隧道可访问 (状态码: {response.status_code})")
    except requests.exceptions.ConnectionError:
        issues.append("Cloudflare 隧道无法连接")
        print("  [FAIL] Cloudflare 隧道无法连接")
        print("         -> 可能原因: Cloudflared 未运行，或隧道未连接")
    except requests.exceptions.SSLError as e:
        issues.append(f"SSL 错误: {e}")
        print(f"  [FAIL] SSL 错误: {e}")
    except requests.exceptions.Timeout:
        issues.append("Cloudflare 隧道超时")
        print("  [FAIL] Cloudflare 隧道超时")
    except Exception as e:
        issues.append(f"Cloudflare 隧道测试失败: {e}")
        print(f"  [FAIL] Cloudflare 隧道测试失败: {e}")
    
    return len(issues) == 0, issues

def check_6_netlify_deployment():
    """检查 6: Netlify 部署状态"""
    print_section("检查 6: Netlify 部署状态")
    
    issues = []
    
    # 检查实际部署的 landing.html
    print("\n  测试 6.1: 检查部署的 landing.html")
    try:
        response = requests.get("https://propkitai.tech/landing.html", timeout=10)
        if response.status_code == 200:
            content = response.text
            print("  [OK] landing.html 可访问")
            
            # 检查版本标识
            if "VERSION 3.0" in content:
                print("  [OK] 找到版本标识 VERSION 3.0 (部署成功)")
            else:
                issues.append("未找到版本标识，可能是旧版本")
                print("  [FAIL] 未找到版本标识 VERSION 3.0")
                print("         -> 可能部署的是旧版本，或未发布")
            
            # 检查 API_WEBHOOK
            if "api.propkitai.tech/api/webhook" in content:
                print("  [OK] 找到正确的 API URL")
            else:
                issues.append("部署的代码中 API URL 可能不正确")
                print("  [WARN] 未找到正确的 API URL")
        else:
            issues.append(f"landing.html 访问失败 (状态码: {response.status_code})")
            print(f"  [FAIL] landing.html 访问失败 (状态码: {response.status_code})")
    except Exception as e:
        issues.append(f"无法检查部署状态: {e}")
        print(f"  [WARN] 无法检查部署状态: {e}")
    
    return len(issues) == 0, issues

def check_7_browser_side():
    """检查 7: 浏览器端可能的问题"""
    print_section("检查 7: 浏览器端可能的问题")
    
    issues = []
    
    print("  7.1: CORS 问题")
    print("       -> 后端已配置 CORS，应该不是问题")
    print("       -> 但如果浏览器控制台有 CORS 错误，需要检查")
    
    print("\n  7.2: 浏览器缓存")
    print("       -> 如果看到旧版本，可能是缓存问题")
    print("       -> 解决方案: Ctrl+F5 强制刷新，或使用无痕窗口")
    
    print("\n  7.3: 网络连接")
    print("       -> 检查浏览器是否能访问 https://api.propkitai.tech")
    print("       -> 检查防火墙是否阻止连接")
    
    print("\n  7.4: JavaScript 错误")
    print("       -> 打开浏览器开发者工具 (F12)")
    print("       -> 查看 Console 标签是否有错误")
    print("       -> 查看 Network 标签，检查 API 请求状态")
    
    return True, []

def main():
    print("\n" + "=" * 70)
    print("  全面诊断 - 检查所有可能的错误点")
    print("=" * 70)
    
    all_issues = {}
    
    # 执行所有检查
    ok1, issues1 = check_1_landing_html_code()
    all_issues["landing.html 代码"] = issues1
    
    ok2, issues2 = check_2_backend_code()
    all_issues["后端代码"] = issues2
    
    ok3, issues3 = check_3_cloudflare_config()
    all_issues["Cloudflare 配置"] = issues3
    
    ok4, issues4 = check_4_runtime_services()
    all_issues["运行时服务"] = issues4
    
    ok5, issues5 = check_5_api_connectivity()
    all_issues["API 连接性"] = issues5
    
    ok6, issues6 = check_6_netlify_deployment()
    all_issues["Netlify 部署"] = issues6
    
    ok7, issues7 = check_7_browser_side()
    all_issues["浏览器端"] = issues7
    
    # 总结
    print_section("诊断总结")
    
    total_issues = sum(len(issues) for issues in all_issues.values())
    
    print(f"\n发现的问题总数: {total_issues}\n")
    
    for category, issues in all_issues.items():
        if issues:
            print(f"  [FAIL] {category}:")
            for issue in issues:
                print(f"         - {issue}")
        else:
            print(f"  [OK] {category}: 无问题")
    
    # 关键问题
    print_section("关键问题分析")
    
    if all_issues["运行时服务"]:
        print("\n  [关键] 运行时服务未运行")
        print("         这是最可能的原因！")
        print("         解决方案:")
        print("         1. 运行: .\\start_services.ps1")
        print("         2. 或运行: .\\一键启动.bat")
        print("         3. 等待 10-15 秒让服务启动")
        print("         4. 再次测试")
    
    if all_issues["Netlify 部署"]:
        print("\n  [关键] Netlify 部署可能有问题")
        print("         解决方案:")
        print("         1. 确认已上传最新 ZIP 文件")
        print("         2. 确认已点击 'Publish deploy'")
        print("         3. 等待 2-5 分钟让 CDN 更新")
        print("         4. 清除浏览器缓存 (Ctrl+F5)")
    
    if all_issues["landing.html 代码"]:
        print("\n  [关键] landing.html 代码有问题")
        print("         需要修复代码后重新打包")
    
    if not any(all_issues.values()):
        print("\n  [OK] 所有检查通过！")
        print("       如果仍然有问题，可能是:")
        print("       1. 浏览器缓存 (尝试 Ctrl+F5)")
        print("       2. 网络问题")
        print("       3. Cloudflare 隧道临时故障")
    
    return total_issues == 0

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
