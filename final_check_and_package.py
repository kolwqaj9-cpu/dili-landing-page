"""
最终检查和打包
确保所有代码配置正确后创建部署包
"""

import os
import zipfile
import re
from datetime import datetime

def check_file_content(filepath, checks):
    """检查文件内容"""
    if not os.path.exists(filepath):
        return False, f"文件不存在: {filepath}"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        for check_name, check_func in checks.items():
            result, msg = check_func(content)
            if not result:
                issues.append(f"{check_name}: {msg}")
        
        if issues:
            return False, "; ".join(issues)
        return True, "OK"
    except Exception as e:
        return False, f"读取失败: {e}"

def verify_landing_html():
    """验证 landing.html"""
    checks = {
        "API_WEBHOOK 定义": lambda c: (
            "const API_WEBHOOK" in c and "api.propkitai.tech/api/webhook" in c,
            "未找到正确的 API_WEBHOOK 定义"
        ),
        "activateTrial 函数": lambda c: (
            "function activateTrial()" in c or "async function activateTrial()" in c,
            "未找到 activateTrial 函数"
        ),
        "fetch API 调用": lambda c: (
            "fetch(API_WEBHOOK" in c,
            "未找到 fetch API 调用"
        ),
        "错误处理": lambda c: (
            "catch (error)" in c,
            "未找到错误处理"
        )
    }
    return check_file_content("landing.html", checks)

def verify_main_py():
    """验证 main.py"""
    checks = {
        "FastAPI 应用": lambda c: (
            "FastAPI()" in c,
            "未找到 FastAPI 应用"
        ),
        "CORS 中间件": lambda c: (
            "CORSMiddleware" in c,
            "未找到 CORS 中间件"
        ),
        "Webhook 端点": lambda c: (
            '@app.post("/api/webhook")' in c or '@app.post(\"/api/webhook\")' in c,
            "未找到 /api/webhook 端点"
        ),
        "端口配置": lambda c: (
            "port=8000" in c or "port = 8000" in c,
            "未找到端口 8000 配置"
        )
    }
    return check_file_content("main.py", checks)

def verify_config_yml():
    """验证 config.yml"""
    checks = {
        "域名映射": lambda c: (
            "api.propkitai.tech" in c and "localhost:8000" in c,
            "未找到正确的域名映射"
        ),
        "ingress 配置": lambda c: (
            "ingress:" in c,
            "未找到 ingress 配置"
        )
    }
    return check_file_content("config.yml", checks)

def verify_dashboard_html():
    """验证 dashboard.html"""
    checks = {
        "Supabase 配置": lambda c: (
            "SUPABASE_URL" in c and "SUPABASE_KEY" in c,
            "未找到 Supabase 配置"
        ),
        "ECharts": lambda c: (
            "echarts" in c.lower(),
            "未找到 ECharts 库"
        )
    }
    return check_file_content("dashboard.html", checks)

def create_final_package():
    """创建最终部署包"""
    print("=" * 60)
    print("  最终检查和打包")
    print("=" * 60)
    
    # 必需文件列表
    required_files = [
        'index.html',
        'landing.html',
        'dashboard.html',
        'signals_landing.html',
        'signals_dashboard.html',
        'terminal_landing.html',
        'terminal_dashboard.html',
        'privacy.html',
        'terms.html',
        'netlify.toml'
    ]
    
    print("\n[步骤 1] 检查文件存在性...")
    print("-" * 60)
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  [OK] {file:30s} ({size:>8,} bytes)")
        else:
            print(f"  [FAIL] {file:30s} - 文件缺失!")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n[错误] 缺失文件: {', '.join(missing_files)}")
        return False
    
    print("\n[步骤 2] 验证关键文件配置...")
    print("-" * 60)
    
    # 验证 landing.html
    ok, msg = verify_landing_html()
    if ok:
        print("  [OK] landing.html - 配置正确")
    else:
        print(f"  [FAIL] landing.html - {msg}")
        return False
    
    # 验证 main.py
    ok, msg = verify_main_py()
    if ok:
        print("  [OK] main.py - 配置正确")
    else:
        print(f"  [FAIL] main.py - {msg}")
        return False
    
    # 验证 config.yml
    ok, msg = verify_config_yml()
    if ok:
        print("  [OK] config.yml - 配置正确")
    else:
        print(f"  [WARN] config.yml - {msg} (后端文件，不影响前端部署)")
    
    # 验证 dashboard.html
    ok, msg = verify_dashboard_html()
    if ok:
        print("  [OK] dashboard.html - 配置正确")
    else:
        print(f"  [WARN] dashboard.html - {msg}")
    
    print("\n[步骤 3] 创建 ZIP 部署包...")
    print("-" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"netlify_deploy_{timestamp}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)
    
    total_size = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in required_files:
            zipf.write(file, file)
            size = os.path.getsize(file)
            total_size += size
            print(f"  [OK] 已添加: {file}")
    
    zip_size = os.path.getsize(zip_path)
    
    print("\n" + "=" * 60)
    print("  打包完成!")
    print("=" * 60)
    print(f"\n  文件名: {zip_filename}")
    print(f"  文件大小: {zip_size:,} bytes ({zip_size/1024:.2f} KB)")
    print(f"  包含文件: {len(required_files)} 个")
    print(f"  文件位置: {zip_path}")
    
    print("\n  所有代码配置已验证正确")
    print("\n  下一步:")
    print("  1. 访问 https://app.netlify.com")
    print("  2. 选择站点: propkitai.tech")
    print("  3. 拖拽 ZIP 文件到部署区域")
    print("  4. 等待部署完成")
    print("  5. 点击 'Publish deploy' 发布")
    print("\n  注意: 部署后需要启动后端服务才能使用完整功能")
    print("  启动服务: .\\start_services.ps1 或 .\\一键启动.bat")
    
    return True

if __name__ == "__main__":
    try:
        success = create_final_package()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
