"""
Check Netlify Deployment Status
Verify if deployment is successful and get latest deploy info
"""

import os
import sys
import json
import requests

def load_config():
    """Load config from file"""
    config_file = '.netlify_config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('api_token', ''), config.get('site_id', '')
        except:
            pass
    return '', ''

def check_deploy_status(api_token, site_id):
    """Check deployment status"""
    print("\n" + "=" * 60)
    print("  Checking Netlify Deployment Status")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    
    try:
        # Get site info
        site_url = f"https://api.netlify.com/api/v1/sites/{site_id}"
        site_response = requests.get(site_url, headers=headers, timeout=30)
        
        if site_response.status_code == 200:
            site_data = site_response.json()
            print(f"\n  Site Name: {site_data.get('name', 'N/A')}")
            print(f"  Site URL: {site_data.get('ssl_url', 'N/A')}")
            published_deploy = site_data.get('published_deploy', {})
            if published_deploy:
                print(f"  Published Deploy ID: {published_deploy.get('id', 'N/A')}")
                print(f"  Published At: {published_deploy.get('published_at', 'N/A')}")
        
        # Get latest deploys
        deploys_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys?per_page=5"
        deploys_response = requests.get(deploys_url, headers=headers, timeout=30)
        
        if deploys_response.status_code == 200:
            deploys = deploys_response.json()
            print(f"\n  Recent Deploys (latest 3):")
            for i, deploy in enumerate(deploys[:3], 1):
                deploy_id = deploy.get('id', 'N/A')
                state = deploy.get('state', 'N/A')
                created_at = deploy.get('created_at', 'N/A')[:19] if deploy.get('created_at') else 'N/A'
                is_published = deploy.get('published_at') is not None
                
                status = "[PUBLISHED]" if is_published else "[DRAFT]"
                print(f"    {i}. {deploy_id[:20]}... {status}")
                print(f"       State: {state}, Created: {created_at}")
        
        # Check live site content
        print(f"\n  Checking live site content...")
        try:
            live_response = requests.get("https://propkitai.tech", timeout=10)
            if live_response.status_code == 200:
                content = live_response.text
                if "PropKit Analytics" in content or "The Science of Certainty" in content:
                    print(f"  [OK] Site shows PropKit content - Deployment successful!")
                elif "Listing Magic" in content:
                    print(f"  [WARN] Site still shows old content (Listing Magic)")
                    print(f"  This is likely a caching issue")
                else:
                    print(f"  [INFO] Site content preview: {content[:150]}...")
        except Exception as e:
            print(f"  [WARN] Could not check live site: {e}")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error checking status: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    api_token, site_id = load_config()
    if not api_token or not site_id:
        print("[FAIL] Configuration not found")
        return False
    
    check_deploy_status(api_token, site_id)
    
    print("\n" + "=" * 60)
    print("  Troubleshooting Tips")
    print("=" * 60)
    print("""
  If site still shows old content:
  
  1. Clear browser cache:
     - Press Ctrl + Shift + Delete
     - Or hard refresh: Ctrl + F5 (Windows) / Cmd + Shift + R (Mac)
  
  2. Wait 2-5 minutes:
     - Netlify CDN needs time to update globally
     - Deployment propagation can take a few minutes
  
  3. Check Netlify Dashboard:
     - Visit: https://app.netlify.com
     - Go to your site
     - Check "Deploys" tab
     - Verify latest deploy is published (green checkmark)
  
  4. Try incognito/private window:
     - This bypasses browser cache completely
  
  5. Check from different network:
     - To rule out local caching issues
    """)

if __name__ == "__main__":
    main()
