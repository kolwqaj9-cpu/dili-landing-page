"""
Netlify 自动上传脚本
使用 Netlify API 直接上传，无需手动拖拽
"""

import os
import sys
import json
import requests
import zipfile
import tempfile
from pathlib import Path

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def get_netlify_config():
    """获取 Netlify 配置"""
    print_section("Step 1: Netlify Configuration")
    
    # 尝试从环境变量或配置文件读取
    api_token = os.environ.get('NETLIFY_API_TOKEN', '')
    site_id = os.environ.get('NETLIFY_SITE_ID', '')
    
    # 如果环境变量没有，尝试从配置文件读取
    if not api_token or not site_id:
        api_token, site_id = load_config()
    
    if not api_token:
        print("  Please provide your Netlify API token")
        print("  You can get it from: https://app.netlify.com/user/applications")
        print()
        api_token = input("  Enter Netlify API Token: ").strip()
    
    if not site_id:
        print("  Please provide your Netlify Site ID")
        print("  You can find it in: Site settings > General > Site details")
        print()
        site_id = input("  Enter Netlify Site ID: ").strip()
    
    if not api_token or not site_id:
        print("  [FAIL] Missing required information")
        return None, None
    
    print(f"  [OK] Using Site ID: {site_id[:20]}...")
    return api_token, site_id

def create_deploy_package():
    """创建部署包"""
    print_section("Step 2: Creating Deploy Package")
    
    files_to_deploy = [
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
    
    # 创建临时 ZIP 文件
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    print(f"  Creating ZIP package...")
    
    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_deploy:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"    Added: {file}")
            else:
                print(f"    [WARN] Missing: {file}")
    
    print(f"  [OK] Package created: {temp_zip.name}")
    return temp_zip.name

def deploy_to_netlify(api_token, site_id, zip_path):
    """上传到 Netlify"""
    print_section("Step 3: Uploading to Netlify")
    
    # Netlify Deploy API endpoint
    deploy_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    
    print(f"  Uploading to: {deploy_url}")
    print(f"  File size: {os.path.getsize(zip_path) / 1024:.2f} KB")
    
    try:
        # 读取 ZIP 文件
        with open(zip_path, 'rb') as f:
            files = {
                'file': ('deploy.zip', f, 'application/zip')
            }
            
            # 上传
            response = requests.post(
                deploy_url,
                headers=headers,
                files=files,
                timeout=300
            )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"  [OK] Upload successful!")
            print(f"  Deploy ID: {result.get('id', 'N/A')}")
            print(f"  Deploy URL: {result.get('deploy_url', 'N/A')}")
            print(f"  Site URL: {result.get('ssl_url', 'N/A')}")
            return True
        else:
            print(f"  [FAIL] Upload failed (Status: {response.status_code})")
            print(f"  Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Upload error: {e}")
        return False
    finally:
        # 清理临时文件
        try:
            os.unlink(zip_path)
        except:
            pass

def save_config(api_token, site_id):
    """保存配置到文件（可选）"""
    config_file = '.netlify_config.json'
    try:
        with open(config_file, 'w') as f:
            json.dump({
                'api_token': api_token,
                'site_id': site_id
            }, f)
        print(f"  [OK] Config saved to {config_file}")
        print(f"  Next time, you won't need to enter these again")
    except:
        pass

def load_config():
    """从文件加载配置"""
    config_file = '.netlify_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('api_token', ''), config.get('site_id', '')
        except:
            pass
    return '', ''

def main():
    print("\n" + "=" * 60)
    print("  Netlify Automatic Upload (No Drag & Drop)")
    print("=" * 60)
    
    # 尝试加载保存的配置
    api_token, site_id = load_config()
    
    # 如果没有配置，获取用户输入
    if not api_token or not site_id:
        api_token, site_id = get_netlify_config()
        if not api_token or not site_id:
            print("\n[FAIL] Configuration incomplete")
            return False
        
        # 保存配置
        save_config(api_token, site_id)
    else:
        print("\n[OK] Using saved configuration")
        print(f"  Site ID: {site_id[:20]}...")
    
    # 创建部署包
    zip_path = create_deploy_package()
    if not zip_path:
        print("\n[FAIL] Failed to create package")
        return False
    
    # 上传
    success = deploy_to_netlify(api_token, site_id, zip_path)
    
    if success:
        print_section("Deployment Complete")
        print("  ✅ Successfully deployed to Netlify!")
        print(f"  Visit: https://propkitai.tech")
        return True
    else:
        print_section("Deployment Failed")
        print("  ❌ Failed to deploy")
        print("  Please check:")
        print("    1. API token is correct")
        print("    2. Site ID is correct")
        print("    3. Internet connection is working")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
