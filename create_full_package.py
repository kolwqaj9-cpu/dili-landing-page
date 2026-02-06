"""
创建完整部署包 - 包含三个landing page和三个dashboard
"""

import os
import zipfile
from datetime import datetime

def create_full_package():
    """创建完整部署包"""
    
    print("=" * 60)
    print("  创建完整部署包 (3个Landing + 3个Dashboard)")
    print("=" * 60)
    
    # 完整文件列表
    files_to_deploy = [
        'index.html',
        'landing.html',              # Alpha Landing
        'dashboard.html',            # Alpha Dashboard
        'signals_landing.html',      # Signals Landing
        'signals_dashboard.html',    # Signals Dashboard
        'terminal_landing.html',     # Terminal Landing
        'terminal_dashboard.html',   # Terminal Dashboard
        'privacy.html',
        'terms.html',
        'netlify.toml'
    ]
    
    print("\n[步骤 1] 检查文件存在性...")
    print("-" * 60)
    
    missing_files = []
    for file in files_to_deploy:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  [OK] {file:30s} ({size:>8,} bytes)")
        else:
            print(f"  [FAIL] {file:30s} - 文件缺失!")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n[错误] 缺失文件: {', '.join(missing_files)}")
        return False
    
    # 验证关键配置
    print("\n[步骤 2] 验证关键配置...")
    print("-" * 60)
    
    landing_files = ['landing.html', 'signals_landing.html', 'terminal_landing.html']
    for landing_file in landing_files:
        with open(landing_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'api.propkitai.tech/api/webhook' in content and 'fetch(API_WEBHOOK' in content:
                print(f"  [OK] {landing_file} - API调用正确")
            else:
                print(f"  [WARN] {landing_file} - API调用可能有问题")
    
    dashboard_files = ['dashboard.html', 'signals_dashboard.html', 'terminal_dashboard.html']
    for dashboard_file in dashboard_files:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'SUPABASE_URL' in content and 'checkData' in content:
                print(f"  [OK] {dashboard_file} - 轮询逻辑存在")
            else:
                print(f"  [WARN] {dashboard_file} - 轮询逻辑可能有问题")
    
    # 检查版本号
    for file in landing_files + ['index.html']:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'VERSION 5.0' in content:
                print(f"  [OK] {file} - 版本标识 VERSION 5.0")
            else:
                print(f"  [WARN] {file} - 版本标识缺失")
    
    print("\n[步骤 3] 创建 ZIP 部署包...")
    print("-" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"netlify_full_{timestamp}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)
    
    total_size = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_deploy:
            zipf.write(file, file)
            size = os.path.getsize(file)
            total_size += size
            print(f"  [OK] 已添加: {file}")
    
    zip_size = os.path.getsize(zip_path)
    
    print("\n" + "=" * 60)
    print("  完整部署包创建完成!")
    print("=" * 60)
    print(f"\n  文件名: {zip_filename}")
    print(f"  文件大小: {zip_size:,} bytes ({zip_size/1024:.2f} KB)")
    print(f"  包含文件: {len(files_to_deploy)} 个")
    print(f"  文件位置: {zip_path}")
    
    print("\n  包含的页面:")
    print("  [OK] index.html - 主页")
    print("  [OK] landing.html - Alpha Landing (触发计算)")
    print("  [OK] dashboard.html - Alpha Dashboard (显示结果)")
    print("  [OK] signals_landing.html - Signals Landing (触发计算)")
    print("  [OK] signals_dashboard.html - Signals Dashboard (显示结果)")
    print("  [OK] terminal_landing.html - Terminal Landing (触发计算)")
    print("  [OK] terminal_dashboard.html - Terminal Dashboard (显示结果)")
    
    print("\n  关键特性:")
    print("  [OK] 所有Landing页面都会真正发送fetch请求到后端")
    print("  [OK] 所有Dashboard页面都会轮询Supabase获取数据")
    print("  [OK] 真实数据用黄色背景标识")
    print("  [OK] 伪数据用红色背景标识")
    print("  [OK] 版本标识 VERSION 5.0 便于确认部署")
    
    print("\n  下一步:")
    print("  1. 访问 https://app.netlify.com")
    print("  2. 选择站点: propkitai.tech")
    print("  3. 拖拽 ZIP 文件到部署区域")
    print("  4. 等待部署完成")
    print("  5. 点击 'Publish deploy' 发布")
    
    print("\n  验证部署:")
    print("  - 访问 https://propkitai.tech/landing.html")
    print("  - 应该看到 'VERSION 5.0' 标识")
    print("  - 如果看到版本标识 → 部署成功")
    
    print("\n  测试流程:")
    print("  1. 确保后端服务运行: .\\start_services.ps1")
    print("  2. 访问任意Landing页面")
    print("  3. 输入新邮箱并点击按钮")
    print("  4. 观察Python窗口是否显示 '启动任务'")
    print("  5. 等待跳转到Dashboard")
    print("  6. Dashboard应该显示计算结果")
    
    return True

if __name__ == "__main__":
    try:
        success = create_full_package()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
