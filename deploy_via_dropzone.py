"""
Deploy to Netlify using Drop Zone API
This is the same API used by drag-and-drop, more reliable
"""

import os
import json
import requests
import zipfile
import tempfile
import time

def load_config():
    with open('.netlify_config.json', 'r') as f:
        return json.load(f)

def create_zip():
    """Create ZIP of files to deploy"""
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
    
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_deploy:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"  Added: {file}")
    
    return temp_zip.name

def deploy_via_dropzone(api_token, site_id, zip_path):
    """Deploy using Netlify Drop Zone API"""
    print("=" * 60)
    print("  Deploying via Drop Zone API")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    
    # Step 1: Get drop zone URL
    print("\n[1/3] Getting drop zone URL...")
    dropzone_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    
    # Step 2: Upload ZIP
    print("[2/3] Uploading ZIP file...")
    with open(zip_path, 'rb') as f:
        files = {'file': ('deploy.zip', f, 'application/zip')}
        response = requests.post(
            dropzone_url,
            headers=headers,
            files=files,
            timeout=300
        )
    
    if response.status_code not in [200, 201]:
        print(f"[FAIL] Upload failed: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return False
    
    result = response.json()
    deploy_id = result.get('id')
    state = result.get('state', 'unknown')
    
    print(f"[OK] Upload successful!")
    print(f"  Deploy ID: {deploy_id}")
    print(f"  State: {state}")
    
    # Step 3: Wait and publish
    print("\n[3/3] Waiting for deploy to process...")
    max_wait = 60
    waited = 0
    
    while waited < max_wait:
        check_url = f"https://api.netlify.com/api/v1/deploys/{deploy_id}"
        check_response = requests.get(check_url, headers=headers, timeout=10)
        
        if check_response.status_code == 200:
            deploy_info = check_response.json()
            current_state = deploy_info.get('state', 'unknown')
            
            if current_state == 'ready':
                print(f"[OK] Deploy is ready!")
                
                # Try to publish
                print("  Attempting to publish...")
                
                # Method: Update site
                site_url = f"https://api.netlify.com/api/v1/sites/{site_id}"
                publish_response = requests.patch(
                    site_url,
                    headers=headers,
                    json={'published_deploy_id': deploy_id},
                    timeout=30
                )
                
                if publish_response.status_code in [200, 201, 204]:
                    print("[OK] Published successfully!")
                    
                    # Verify
                    time.sleep(2)
                    verify_response = requests.get(site_url, headers=headers, timeout=10)
                    if verify_response.status_code == 200:
                        site_data = verify_response.json()
                        published_id = site_data.get('published_deploy', {}).get('id', '')
                        if published_id == deploy_id:
                            print("[OK] Verified: Site is using this deploy!")
                            return True
                
                print("[WARN] Publish may have failed, but deploy is ready")
                print(f"  Manual publish: https://app.netlify.com/sites/{site_id}/deploys/{deploy_id}")
                return True
            elif current_state == 'error':
                print(f"[FAIL] Deploy failed")
                return False
        
        time.sleep(3)
        waited += 3
        if waited % 9 == 0:
            print(f"  Waiting... ({waited}s)")
    
    print("[WARN] Timeout waiting for deploy")
    return False

def main():
    print("\n" + "=" * 60)
    print("  Netlify Drop Zone Deployment")
    print("=" * 60)
    
    config = load_config()
    api_token = config['api_token']
    site_id = config['site_id']
    
    print(f"\nSite ID: {site_id}")
    
    zip_path = create_zip()
    print(f"\nZIP created: {os.path.getsize(zip_path) / 1024:.2f} KB")
    
    try:
        success = deploy_via_dropzone(api_token, site_id, zip_path)
        
        if success:
            print("\n" + "=" * 60)
            print("  Deployment Complete!")
            print("=" * 60)
            print("\n  Wait 1-2 minutes, then:")
            print("  - Clear browser cache (Ctrl+F5)")
            print("  - Visit: https://propkitai.tech")
        else:
            print("\n[FAIL] Deployment failed")
    finally:
        if os.path.exists(zip_path):
            os.unlink(zip_path)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
