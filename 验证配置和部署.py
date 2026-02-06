"""
验证 Netlify 配置和部署状态
检查 token、site_id 是否正确，以及部署是否成功
"""

import json
import requests

def verify_config():
    """验证配置"""
    print("=" * 60)
    print("  Verifying Netlify Configuration")
    print("=" * 60)
    
    try:
        with open('.netlify_config.json', 'r') as f:
            config = json.load(f)
        
        api_token = config.get('api_token', '')
        site_id = config.get('site_id', '')
        
        print(f"\nAPI Token: {api_token[:20]}...{api_token[-10:]}")
        print(f"Site ID: {site_id}")
        
        return api_token, site_id
    except Exception as e:
        print(f"[FAIL] Error reading config: {e}")
        return None, None

def verify_token(api_token):
    """验证 token 是否有效"""
    print("\n" + "=" * 60)
    print("  Verifying API Token")
    print("=" * 60)
    
    headers = {'Authorization': f'Bearer {api_token}'}
    
    try:
        # 获取用户信息
        user_url = "https://api.netlify.com/api/v1/user"
        response = requests.get(user_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"[OK] Token is valid")
            print(f"  User: {user_data.get('email', 'N/A')}")
            print(f"  User ID: {user_data.get('id', 'N/A')}")
            return True
        elif response.status_code == 401:
            print(f"[FAIL] Token is invalid or expired")
            print(f"  Status: 401 Unauthorized")
            return False
        else:
            print(f"[WARN] Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] Error verifying token: {e}")
        return False

def verify_site(api_token, site_id):
    """验证站点 ID 是否正确"""
    print("\n" + "=" * 60)
    print("  Verifying Site ID")
    print("=" * 60)
    
    headers = {'Authorization': f'Bearer {api_token}'}
    
    try:
        site_url = f"https://api.netlify.com/api/v1/sites/{site_id}"
        response = requests.get(site_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            site_data = response.json()
            print(f"[OK] Site ID is valid")
            print(f"  Site Name: {site_data.get('name', 'N/A')}")
            print(f"  Site URL: {site_data.get('ssl_url', 'N/A')}")
            print(f"  Custom Domain: {site_data.get('custom_domain', 'N/A')}")
            
            # 检查域名是否匹配
            custom_domain = site_data.get('custom_domain', '')
            if 'propkitai.tech' in custom_domain or site_data.get('ssl_url', '').endswith('propkitai.tech'):
                print(f"[OK] Domain matches: propkitai.tech")
            else:
                print(f"[WARN] Domain may not match!")
                print(f"  Expected: propkitai.tech")
                print(f"  Found: {custom_domain or site_data.get('ssl_url', 'N/A')}")
            
            return True, site_data
        elif response.status_code == 404:
            print(f"[FAIL] Site ID not found")
            print(f"  Status: 404 Not Found")
            print(f"  The Site ID may be incorrect")
            return False, None
        else:
            print(f"[FAIL] Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        print(f"[FAIL] Error verifying site: {e}")
        return False, None

def check_deploys(api_token, site_id):
    """检查部署列表"""
    print("\n" + "=" * 60)
    print("  Checking Recent Deploys")
    print("=" * 60)
    
    headers = {'Authorization': f'Bearer {api_token}'}
    
    try:
        deploys_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys?per_page=5"
        response = requests.get(deploys_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            deploys = response.json()
            print(f"[OK] Found {len(deploys)} recent deploys\n")
            
            for i, deploy in enumerate(deploys[:5], 1):
                deploy_id = deploy.get('id', 'N/A')
                state = deploy.get('state', 'N/A')
                created_at = deploy.get('created_at', 'N/A')[:19] if deploy.get('created_at') else 'N/A'
                published_at = deploy.get('published_at', 'N/A')[:19] if deploy.get('published_at') else None
                
                status = "[PUBLISHED]" if published_at else "[DRAFT]"
                print(f"  {i}. {deploy_id[:24]}...")
                print(f"     State: {state}")
                print(f"     Created: {created_at}")
                print(f"     Published: {published_at or 'Not published'}")
                print(f"     Status: {status}")
                print()
            
            return deploys
        else:
            print(f"[FAIL] Failed to get deploys: {response.status_code}")
            return []
    except Exception as e:
        print(f"[FAIL] Error checking deploys: {e}")
        return []

def check_live_site():
    """检查实际网站内容"""
    print("\n" + "=" * 60)
    print("  Checking Live Site Content")
    print("=" * 60)
    
    try:
        response = requests.get("https://propkitai.tech", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            print(f"  Status Code: {response.status_code}")
            
            if "PropKit Analytics" in content or "The Science of Certainty" in content:
                print(f"  [OK] Site shows PropKit content - Deployment successful!")
                return True
            elif "Listing Magic" in content:
                print(f"  [FAIL] Site still shows old content (Listing Magic)")
                print(f"  This means deployment did not update the site")
                return False
            else:
                print(f"  [INFO] Site content preview:")
                print(f"  {content[:200]}...")
                return None
        else:
            print(f"  [WARN] Unexpected status: {response.status_code}")
            return None
    except Exception as e:
        print(f"  [FAIL] Error checking site: {e}")
        return None

def main():
    print("\n" + "=" * 60)
    print("  Netlify Configuration and Deployment Verification")
    print("=" * 60)
    
    # Step 1: Load config
    api_token, site_id = verify_config()
    if not api_token or not site_id:
        print("\n[FAIL] Configuration incomplete")
        return False
    
    # Step 2: Verify token
    if not verify_token(api_token):
        print("\n[FAIL] API Token is invalid!")
        print("  Please check your token in .netlify_config.json")
        print("  Get new token from: https://app.netlify.com/user/applications")
        return False
    
    # Step 3: Verify site
    site_valid, site_data = verify_site(api_token, site_id)
    if not site_valid:
        print("\n[FAIL] Site ID is invalid!")
        print("  Please check your Site ID in .netlify_config.json")
        print("  Find it in: Site settings > General > Site details")
        return False
    
    # Step 4: Check deploys
    deploys = check_deploys(api_token, site_id)
    
    # Step 5: Check live site
    live_status = check_live_site()
    
    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    
    if site_valid:
        print(f"  [OK] Configuration is valid")
        print(f"  [OK] Token is valid")
        print(f"  [OK] Site ID is valid")
        
        if deploys:
            latest = deploys[0]
            if latest.get('published_at'):
                print(f"  [OK] Latest deploy is published")
            else:
                print(f"  [WARN] Latest deploy is NOT published (DRAFT)")
                print(f"  You need to publish it manually in Netlify dashboard")
        
        if live_status is False:
            print(f"  [FAIL] Live site still shows old content")
            print(f"  This means:")
            print(f"    1. Deployment may not have been published")
            print(f"    2. Or deployment went to wrong site")
            print(f"    3. Or CDN cache needs more time")
        
        print(f"\n  Next steps:")
        if deploys and not deploys[0].get('published_at'):
            latest_id = deploys[0].get('id', '')
            print(f"    1. Publish latest deploy:")
            print(f"       https://app.netlify.com/sites/{site_id}/deploys/{latest_id}")
        print(f"    2. Wait 2-5 minutes after publishing")
        print(f"    3. Clear browser cache (Ctrl+F5)")
        print(f"    4. Check site again")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
