"""
Netlify Deploy and Publish Script
Upload files and ensure they are published
"""

import os
import sys
import json
import requests
import zipfile
import tempfile
import time

def load_config():
    config_file = '.netlify_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('api_token', ''), config.get('site_id', '')
        except:
            pass
    return '', ''

def deploy_and_publish():
    api_token, site_id = load_config()
    if not api_token or not site_id:
        print("[FAIL] Configuration not found")
        return False
    
    headers = {'Authorization': f'Bearer {api_token}'}
    
    # Files to deploy
    files_to_deploy = [
        'index.html', 'landing.html', 'dashboard.html',
        'signals_landing.html', 'signals_dashboard.html',
        'terminal_landing.html', 'terminal_dashboard.html',
        'privacy.html', 'terms.html', 'netlify.toml'
    ]
    
    # Create ZIP
    print("Creating deployment package...")
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_deploy:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"  Added: {file}")
    
    # Upload ZIP
    print(f"\nUploading to Netlify...")
    drop_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    
    with open(temp_zip.name, 'rb') as f:
        files = {'file': ('deploy.zip', f, 'application/zip')}
        response = requests.post(drop_url, headers=headers, files=files, timeout=300)
    
    if response.status_code not in [200, 201]:
        print(f"[FAIL] Upload failed: {response.status_code}")
        print(response.text[:500])
        return False
    
    result = response.json()
    deploy_id = result.get('id')
    print(f"[OK] Upload successful! Deploy ID: {deploy_id}")
    
    # Wait for deploy to be ready
    print(f"\nWaiting for deploy to process...")
    max_wait = 60
    waited = 0
    
    while waited < max_wait:
        check_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}"
        check_response = requests.get(check_url, headers=headers, timeout=30)
        
        if check_response.status_code == 200:
            deploy_info = check_response.json()
            state = deploy_info.get('state', 'unknown')
            
            if state == 'ready':
                print(f"[OK] Deploy is ready! Publishing...")
                break
            elif state == 'error':
                print(f"[FAIL] Deploy failed")
                return False
        
        time.sleep(3)
        waited += 3
        if waited % 9 == 0:
            print(f"  Still processing... ({waited}s)")
    
    # Publish the deploy
    print(f"\nPublishing deploy...")
    publish_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}/restore"
    publish_response = requests.post(publish_url, headers=headers, timeout=30)
    
    if publish_response.status_code in [200, 201, 204]:
        print(f"[OK] Deploy published successfully!")
        
        # Verify
        time.sleep(3)
        verify_response = requests.get(check_url, headers=headers, timeout=30)
        if verify_response.status_code == 200:
            verify_info = verify_response.json()
            if verify_info.get('published_at'):
                print(f"[OK] Verified: Deploy is published!")
                print(f"\nSite URL: https://propkitai.tech")
                print(f"Please wait 1-2 minutes for CDN to update, then:")
                print(f"  - Clear browser cache (Ctrl+F5)")
                print(f"  - Or use incognito window")
                return True
        
        print(f"[OK] Deploy should be published")
        return True
    else:
        # Try alternative method
        print(f"Trying alternative publish method...")
        update_url = f"https://api.netlify.com/api/v1/sites/{site_id}"
        update_data = {'published_deploy_id': deploy_id}
        update_response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
        
        if update_response.status_code in [200, 201, 204]:
            print(f"[OK] Site updated to use this deploy!")
            print(f"\nSite URL: https://propkitai.tech")
            print(f"Note: May take 1-2 minutes to propagate")
            return True
        else:
            print(f"[WARN] Automatic publish failed")
            print(f"Please manually publish in Netlify dashboard:")
            print(f"https://app.netlify.com/sites/{site_id}/deploys/{deploy_id}")
            return False
    
    # Cleanup
    try:
        os.unlink(temp_zip.name)
    except:
        pass

if __name__ == "__main__":
    try:
        success = deploy_and_publish()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
