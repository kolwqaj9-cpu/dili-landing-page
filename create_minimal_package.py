"""
创建最小化核心部署包
只包含核心功能：主页、landing、dashboard
"""

import os
import zipfile
from datetime import datetime

def create_minimal_package():
    """创建最小化部署包"""
    
    print("=" * 60)
    print("  创建最小化核心部署包")
    print("=" * 60)
    
    # 核心文件列表（最小化）
    core_files = [
        'index.html',      # 主页
        'landing.html',    # 核心功能页面
        'dashboard.html',  # 结果页面
        'netlify.toml'     # Netlify 配置
    ]
    
    print("\n[步骤 1] 检查核心文件...")
    print("-" * 60)
    
    missing_files = []
    for file in core_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  [OK] {file:25s} ({size:>8,} bytes)")
        else:
            print(f"  [FAIL] {file:25s} - 文件缺失!")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n[错误] 缺失核心文件: {', '.join(missing_files)}")
        return False
    
    # 验证关键配置
    print("\n[步骤 2] 验证关键配置...")
    print("-" * 60)
    
    # 检查 landing.html 中的 API 配置
    with open('landing.html', 'r', encoding='utf-8') as f:
        landing_content = f.read()
        if 'api.propkitai.tech/api/webhook' in landing_content:
            print("  [OK] landing.html - API 配置正确")
        else:
            print("  [FAIL] landing.html - API 配置缺失")
            return False
        
        if 'VERSION 3.0' in landing_content:
            print("  [OK] landing.html - 版本标识存在")
        else:
            print("  [WARN] landing.html - 版本标识缺失")
    
    # 检查 index.html 中的版本标识
    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()
        if 'VERSION 3.0' in index_content:
            print("  [OK] index.html - 版本标识存在")
        else:
            print("  [WARN] index.html - 版本标识缺失")
    
    print("\n[步骤 3] 创建 ZIP 部署包...")
    print("-" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"netlify_core_{timestamp}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)
    
    total_size = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in core_files:
            zipf.write(file, file)
            size = os.path.getsize(file)
            total_size += size
            print(f"  [OK] 已添加: {file}")
    
    zip_size = os.path.getsize(zip_path)
    
    print("\n" + "=" * 60)
    print("  最小化核心包创建完成!")
    print("=" * 60)
    print(f"\n  文件名: {zip_filename}")
    print(f"  文件大小: {zip_size:,} bytes ({zip_size/1024:.2f} KB)")
    print(f"  包含文件: {len(core_files)} 个核心文件")
    print(f"  文件位置: {zip_path}")
    
    print("\n  核心功能:")
    print("  [OK] 主页 (index.html) - 带版本标识")
    print("  [OK] Landing 页面 (landing.html) - 核心功能，带版本标识")
    print("  [OK] Dashboard 页面 (dashboard.html) - 结果显示")
    print("  [OK] Netlify 配置 (netlify.toml) - API 代理")
    
    print("\n  下一步:")
    print("  1. 访问 https://app.netlify.com")
    print("  2. 选择站点: propkitai.tech")
    print("  3. 拖拽 ZIP 文件到部署区域")
    print("  4. 等待部署完成")
    print("  5. 点击 'Publish deploy' 发布")
    print("\n  验证部署:")
    print("  - 访问 https://propkitai.tech/landing.html")
    print("  - 应该看到 'VERSION 3.0' 标识")
    print("  - 如果看到版本标识 → 部署成功")
    
    print("\n  注意:")
    print("  - 这是最小化版本，只包含核心功能")
    print("  - 连接功能需要后端服务运行")
    print("  - 启动服务: .\\start_services.ps1")
    
    return True

if __name__ == "__main__":
    try:
        success = create_minimal_package()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
