"""
Verify Netlify Configuration and Deployment
Check if token, site_id are correct and deployment status
"""

import json
import requests

def verify_config():
    """Verify configuration"""
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
    """Verify token is valid"""
    print("\n" + "=" * 60)
    print("  Verifying API Token")
    print("=" * 60)
    
    headers = {'Authorization': f'Bearer {api_token}'}
    
    try:
        user_url = "https://api.netlify.com/api/v1/user"
        response = requests.get(user_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"[OK] Token is valid")
            print(f"  User: {user_data.get('email', 'N/A')}")
            return True
        elif response.status_code == 401:
            print(f"[FAIL] Token is invalid or expired")
            return False
        else:
            print(f"[WARN] Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def verify_site(api_token, site_id):
    """Verify site ID is correct"""
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
            
            custom_domain = site_data.get('custom_domain', '')
            ssl_url = site_data.get('ssl_url', '')
            
            if 'propkitai.tech' in custom_domain or 'propkitai.tech' in ssl_url:
                print(f"[OK] Domain matches: propkitai.tech")
            else:
                print(f"[WARN] Domain may not match!")
                print(f"  Expected: propkitai.tech")
                print(f"  Found: {custom_domain or ssl_url}")
            
            return True, site_data
        elif response.status_code == 404:
            print(f"[FAIL] Site ID not found (404)")
            print(f"  The Site ID may be incorrect")
            return False, None
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False, None

def check_deploys(api_token, site_id):
    """Check deployment list"""
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
            
            for i, deploy in enumerate(deploys[:3], 1):
                deploy_id = deploy.get('id', 'N/A')
                state = deploy.get('state', 'N/A')
                created_at = deploy.get('created_at', 'N/A')[:19] if deploy.get('created_at') else 'N/A'
                published_at = deploy.get('published_at')
                
                status = "[PUBLISHED]" if published_at else "[DRAFT]"
                print(f"  {i}. Deploy ID: {deploy_id[:24]}...")
                print(f"     State: {state}, Status: {status}")
                print(f"     Created: {created_at}")
                if published_at:
                    print(f"     Published: {published_at[:19]}")
                print()
            
            return deploys
        else:
            print(f"[FAIL] Failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return []

def check_live_site():
    """Check actual website content"""
    print("\n" + "=" * 60)
    print("  Checking Live Site Content")
    print("=" * 60)
    
    try:
        response = requests.get("https://propkitai.tech", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            print(f"  Status: {response.status_code}")
            
            if "PropKit Analytics" in content or "The Science of Certainty" in content:
                print(f"  [OK] Site shows PropKit content!")
                return True
            elif "Listing Magic" in content:
                print(f"  [FAIL] Site shows old content (Listing Magic)")
                print(f"  Deployment did not update the site")
                return False
            else:
                print(f"  [INFO] Content preview: {content[:150]}...")
                return None
        else:
            print(f"  [WARN] Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return None

def main():
    print("\n" + "=" * 60)
    print("  Netlify Configuration Verification")
    print("=" * 60)
    
    api_token, site_id = verify_config()
    if not api_token or not site_id:
        print("\n[FAIL] Configuration incomplete")
        return
    
    if not verify_token(api_token):
        print("\n[FAIL] API Token is INVALID!")
        print("  Please get a new token from:")
        print("  https://app.netlify.com/user/applications")
        return
    
    site_valid, site_data = verify_site(api_token, site_id)
    if not site_valid:
        print("\n[FAIL] Site ID is INVALID!")
        print("  Please check Site ID in:")
        print("  Site settings > General > Site details")
        return
    
    deploys = check_deploys(api_token, site_id)
    live_status = check_live_site()
    
    print("\n" + "=" * 60)
    print("  Summary and Next Steps")
    print("=" * 60)
    
    if site_valid:
        print(f"\n  [OK] Configuration is VALID")
        
        if deploys:
            latest = deploys[0]
            if latest.get('published_at'):
                print(f"  [OK] Latest deploy is PUBLISHED")
            else:
                print(f"  [WARN] Latest deploy is DRAFT (not published)")
                latest_id = latest.get('id', '')
                print(f"\n  To publish manually:")
                print(f"  https://app.netlify.com/sites/{site_id}/deploys/{latest_id}")
        
        if live_status is False:
            print(f"\n  [FAIL] Live site still shows old content")
            print(f"  Possible reasons:")
            print(f"    1. Latest deploy is not published (check above)")
            print(f"    2. CDN cache (wait 2-5 minutes)")
            print(f"    3. Wrong site ID (but verification passed)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
