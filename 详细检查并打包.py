"""
详细检查所有文件并创建部署包
"""

import os
import zipfile
from datetime import datetime

def check_file(filepath, required=True):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    if exists:
        size = os.path.getsize(filepath)
        return True, size
    else:
        return False, 0

def verify_file_content(filepath, keywords):
    """验证文件内容包含关键词"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            for keyword in keywords:
                if keyword not in content:
                    return False, f"Missing keyword: {keyword}"
            return True, "OK"
    except Exception as e:
        return False, str(e)

def create_deploy_zip():
    """创建部署包"""
    
    print("=" * 60)
    print("  详细检查并创建部署包")
    print("=" * 60)
    
    # 必需文件列表
    required_files = {
        'index.html': {
            'keywords': ['PropKit Analytics', 'The Science of Certainty'],
            'description': '主页'
        },
        'landing.html': {
            'keywords': ['API_WEBHOOK', 'api.propkitai.tech', 'activateTrial'],
            'description': 'Alpha Landing 页面'
        },
        'dashboard.html': {
            'keywords': ['COMMANDER', 'ALPHA DASHBOARD', 'SUPABASE_URL'],
            'description': 'Alpha Dashboard 页面'
        },
        'signals_landing.html': {
            'keywords': ['PropKit AI', 'activateIntent'],
            'description': 'Signals Landing 页面'
        },
        'signals_dashboard.html': {
            'keywords': ['dashboard', 'PropKit'],
            'description': 'Signals Dashboard 页面'
        },
        'terminal_landing.html': {
            'keywords': ['PropKit API', 'showPricing'],
            'description': 'Terminal Landing 页面'
        },
        'terminal_dashboard.html': {
            'keywords': ['dashboard', 'PropKit'],
            'description': 'Terminal Dashboard 页面'
        },
        'privacy.html': {
            'keywords': ['Privacy', 'Policy'],
            'description': '隐私政策'
        },
        'terms.html': {
            'keywords': ['Terms', 'Service'],
            'description': '服务条款'
        },
        'netlify.toml': {
            'keywords': ['[build]', 'publish'],
            'description': 'Netlify 配置'
        }
    }
    
    print("\n[步骤 1] 检查文件存在性...")
    print("-" * 60)
    
    all_ok = True
    file_status = {}
    
    for filename, config in required_files.items():
        exists, size = check_file(filename)
        if exists:
            print(f"  [OK] {filename:25s} ({size:>8,} bytes) - {config['description']}")
            file_status[filename] = {'exists': True, 'size': size}
        else:
            print(f"  [FAIL] {filename:25s} - 文件缺失!")
            file_status[filename] = {'exists': False, 'size': 0}
            all_ok = False
    
    if not all_ok:
        print("\n[错误] 有必需文件缺失，无法继续打包")
        return False
    
    print("\n[步骤 2] 验证文件内容...")
    print("-" * 60)
    
    content_ok = True
    for filename, config in required_files.items():
        if file_status[filename]['exists']:
            ok, msg = verify_file_content(filename, config['keywords'])
            if ok:
                print(f"  [OK] {filename:25s} - 内容验证通过")
            else:
                print(f"  [WARN] {filename:25s} - {msg}")
                content_ok = False
    
    print("\n[步骤 3] 创建 ZIP 部署包...")
    print("-" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"netlify_deploy_{timestamp}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)
    
    total_size = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in required_files.keys():
            if file_status[filename]['exists']:
                zipf.write(filename, filename)
                total_size += file_status[filename]['size']
                print(f"  [OK] 已添加: {filename}")
    
    zip_size = os.path.getsize(zip_path)
    
    print("\n" + "=" * 60)
    print("  打包完成!")
    print("=" * 60)
    print(f"\n  文件名: {zip_filename}")
    print(f"  文件大小: {zip_size:,} bytes ({zip_size/1024:.2f} KB)")
    print(f"  包含文件: {len(required_files)} 个")
    print(f"  文件位置: {zip_path}")
    
    print("\n  下一步:")
    print("  1. 访问 https://app.netlify.com")
    print("  2. 选择站点: propkitai.tech")
    print("  3. 拖拽 ZIP 文件到部署区域")
    print("  4. 等待部署完成")
    print("  5. 点击 'Publish deploy' 发布")
    
    return True

if __name__ == "__main__":
    try:
        success = create_deploy_zip()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
