"""
Publish Latest Netlify Deploy
Force publish the latest deployment
"""

import json
import requests
import time

def load_config():
    with open('.netlify_config.json', 'r') as f:
        return json.load(f)

def publish_latest_deploy():
    config = load_config()
    api_token = config['api_token']
    site_id = config['site_id']
    headers = {'Authorization': f'Bearer {api_token}'}
    
    print("=" * 60)
    print("  Publishing Latest Deploy")
    print("=" * 60)
    
    # Get latest deploy
    print("\nGetting latest deploy...")
    deploys_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys?per_page=1"
    response = requests.get(deploys_url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"[FAIL] Failed to get deploys: {response.status_code}")
        return False
    
    deploys = response.json()
    if not deploys:
        print("[FAIL] No deploys found")
        return False
    
    latest = deploys[0]
    deploy_id = latest.get('id')
    
    print(f"[OK] Latest deploy ID: {deploy_id}")
    print(f"  State: {latest.get('state', 'N/A')}")
    print(f"  Published: {latest.get('published_at') is not None}")
    
    if latest.get('published_at'):
        print("[OK] Deploy is already published!")
        return True
    
    # Wait for deploy to be ready
    print("\nWaiting for deploy to be ready...")
    max_wait = 30
    waited = 0
    
    while waited < max_wait:
        check_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}"
        check_response = requests.get(check_url, headers=headers, timeout=10)
        
        if check_response.status_code == 200:
            deploy_info = check_response.json()
            state = deploy_info.get('state', 'unknown')
            
            if state in ['ready', 'new']:
                print(f"[OK] Deploy is ready (state: {state})")
                break
            elif state == 'error':
                print(f"[FAIL] Deploy failed")
                return False
        
        time.sleep(2)
        waited += 2
        if waited % 6 == 0:
            print(f"  Waiting... ({waited}s)")
    
    # Try multiple publish methods
    print("\nAttempting to publish...")
    
    # Method 1: Restore endpoint
    print("  Method 1: Using restore endpoint...")
    restore_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}/restore"
    restore_response = requests.post(restore_url, headers=headers, timeout=30)
    
    if restore_response.status_code in [200, 201, 204]:
        print("  [OK] Restore method succeeded!")
        time.sleep(3)
        
        # Verify
        verify_response = requests.get(f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}", headers=headers, timeout=10)
        if verify_response.status_code == 200:
            verify_info = verify_response.json()
            if verify_info.get('published_at'):
                print("  [OK] Verified: Deploy is now published!")
                return True
    
    # Method 2: Update site published_deploy_id
    print("  Method 2: Updating site published_deploy_id...")
    update_url = f"https://api.netlify.com/api/v1/sites/{site_id}"
    update_data = {'published_deploy_id': deploy_id}
    update_response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
    
    if update_response.status_code in [200, 201, 204]:
        print("  [OK] Site updated successfully!")
        time.sleep(3)
        
        # Verify site
        site_response = requests.get(update_url, headers=headers, timeout=10)
        if site_response.status_code == 200:
            site_data = site_response.json()
            published_id = site_data.get('published_deploy', {}).get('id', '')
            if published_id == deploy_id:
                print("  [OK] Verified: Site is using this deploy!")
                return True
    
    # Method 3: Lock and restore
    print("  Method 3: Lock and restore...")
    lock_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}/lock"
    lock_response = requests.post(lock_url, headers=headers, json={'locked': True}, timeout=30)
    
    if lock_response.status_code in [200, 201, 204]:
        time.sleep(1)
        restore_response2 = requests.post(restore_url, headers=headers, timeout=30)
        if restore_response2.status_code in [200, 201, 204]:
            print("  [OK] Lock and restore succeeded!")
            return True
    
    print("\n[WARN] Automatic publish failed")
    print(f"Please publish manually:")
    print(f"https://app.netlify.com/sites/{site_id}/deploys/{deploy_id}")
    return False

if __name__ == "__main__":
    try:
        success = publish_latest_deploy()
        if success:
            print("\n" + "=" * 60)
            print("  Publishing Complete!")
            print("=" * 60)
            print("\n  Wait 1-2 minutes, then:")
            print("  - Clear browser cache (Ctrl+F5)")
            print("  - Or use incognito window")
            print("  - Visit: https://propkitai.tech")
        else:
            print("\n[FAIL] Could not publish automatically")
            print("Please publish manually in Netlify dashboard")
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
