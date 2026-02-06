"""
Check actual website status and deployment
"""

import json
import requests

def check_live_site():
    """Check what's actually on the live site"""
    print("=" * 60)
    print("  Checking Live Website Content")
    print("=" * 60)
    
    try:
        # Check root (index.html)
        print("\n[1] Checking root (https://propkitai.tech/)...")
        response = requests.get("https://propkitai.tech/", timeout=10)
        if response.status_code == 200:
            content = response.text
            print(f"  Status: {response.status_code}")
            
            if "PropKit Analytics" in content or "The Science of Certainty" in content:
                print("  [OK] Root shows NEW PropKit content!")
                return True
            elif "Listing Magic" in content:
                print("  [FAIL] Root still shows OLD content (Listing Magic)")
                print("  [INFO] First 200 chars:", content[:200])
                return False
            else:
                print("  [WARN] Content is unexpected")
                print("  [INFO] First 200 chars:", content[:200])
                return None
        else:
            print(f"  [FAIL] Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return None

def check_landing():
    """Check landing page"""
    print("\n[2] Checking landing page (https://propkitai.tech/landing.html)...")
    try:
        response = requests.get("https://propkitai.tech/landing.html", timeout=10)
        if response.status_code == 200:
            print(f"  [OK] Landing page accessible (Status: {response.status_code})")
            if "Special Offer: 1 Month Free Trial" in response.text:
                print("  [OK] Landing page shows correct content")
                return True
        else:
            print(f"  [WARN] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False

def check_deployments():
    """Check latest deployments"""
    print("\n" + "=" * 60)
    print("  Checking Latest Deployments")
    print("=" * 60)
    
    try:
        with open('.netlify_config.json', 'r') as f:
            config = json.load(f)
        
        headers = {'Authorization': f'Bearer {config["api_token"]}'}
        site_id = config['site_id']
        
        # Get latest deploys
        deploys_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys?per_page=3"
        response = requests.get(deploys_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            deploys = response.json()
            print(f"\n  Found {len(deploys)} recent deploys:\n")
            
            for i, deploy in enumerate(deploys[:3], 1):
                deploy_id = deploy.get('id', 'N/A')
                state = deploy.get('state', 'N/A')
                created_at = deploy.get('created_at', 'N/A')[:19] if deploy.get('created_at') else 'N/A'
                published_at = deploy.get('published_at')
                
                status = "[PUBLISHED]" if published_at else "[DRAFT]"
                print(f"  {i}. {deploy_id[:24]}...")
                print(f"     State: {state}, Status: {status}")
                print(f"     Created: {created_at}")
                if published_at:
                    print(f"     Published: {published_at[:19]}")
                print()
            
            # Check which deploy is actually published
            site_url = f"https://api.netlify.com/api/v1/sites/{site_id}"
            site_response = requests.get(site_url, headers=headers, timeout=10)
            if site_response.status_code == 200:
                site_data = site_response.json()
                published_deploy_id = site_data.get('published_deploy', {}).get('id', 'N/A')
                print(f"  Currently published deploy: {published_deploy_id[:24]}...")
                
                # Check if latest deploy is published
                if deploys and deploys[0].get('id') == published_deploy_id:
                    print("  [OK] Latest deploy is published")
                else:
                    print("  [WARN] Latest deploy is NOT the published one")
                    if published_deploy_id != 'N/A':
                        print(f"  [INFO] You need to publish the latest deploy")
                        print(f"  https://app.netlify.com/sites/{site_id}/deploys/{deploys[0].get('id')}")
            
            return deploys
        else:
            print(f"  [FAIL] Failed to get deploys: {response.status_code}")
            return []
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return []

def main():
    print("\n" + "=" * 60)
    print("  Website Status Check")
    print("=" * 60)
    
    # Check live site
    root_status = check_live_site()
    landing_status = check_landing()
    
    # Check deployments
    deploys = check_deployments()
    
    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    
    if root_status is True:
        print("\n  [OK] Root page (index.html) shows NEW content!")
        print("  Deployment successful!")
    elif root_status is False:
        print("\n  [FAIL] Root page still shows OLD content")
        print("  Possible reasons:")
        print("    1. Latest deploy is not published (check above)")
        print("    2. CDN cache (wait 2-5 minutes)")
        print("    3. Browser cache (try Ctrl+F5 or incognito)")
    
    if landing_status:
        print("  [OK] Landing page is working correctly")
    
    if deploys:
        latest = deploys[0]
        if not latest.get('published_at'):
            print("\n  [ACTION REQUIRED]")
            print("  Latest deploy needs to be published:")
            print(f"  https://app.netlify.com/sites/{json.load(open('.netlify_config.json'))['site_id']}/deploys/{latest.get('id')}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
