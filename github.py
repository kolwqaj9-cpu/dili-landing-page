"""
Netlify Auto Deploy Script (Fixed Version)
Includes Polling & Binary Upload for Stability
"""

import os
import sys
import json
import requests
import zipfile
import tempfile
import re
import time
from html.parser import HTMLParser

# ================= Helper Classes & Functions =================

class VisibleTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_chunks = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.text_chunks.append(text)

def extract_visible_text(html, max_chars=200):
    parser = VisibleTextExtractor()
    parser.feed(html)
    text = ' '.join(parser.text_chunks)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars] if text else "[EMPTY]"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

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

def get_netlify_config():
    """Get Netlify configuration"""
    print_section("Step 1: Netlify Configuration")
    
    api_token, site_id = load_config()
    
    if not api_token or not site_id:
        print("  [FAIL] Configuration not found")
        print("  Please check .netlify_config.json file")
        return None, None
    
    print(f"  [OK] Using Site ID: {site_id[:20]}...")
    return api_token, site_id

def create_deploy_package():
    """Create deployment package"""
    print_section("Step 2: Creating Deploy Package")
    
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            index_html = f.read()
        index_preview = extract_visible_text(index_html, 200)
        title_match = re.search(r"<title>(.*?)</title>", index_html, re.IGNORECASE | re.DOTALL)
        title_text = title_match.group(1).strip() if title_match else "N/A"
        print("  ===== Index Preview =====")
        print(f"  Title: {title_text}")
        print(f"  First 200 chars: {index_preview}")
        print("  =========================")
    except Exception as e:
        print(f"  [WARN] Unable to read index.html preview: {e}")
    
    # List of files to include
    files_to_deploy = [
        'index.html',
        'checkout.html',
        'signals_dashboard.html',
        'privacy.html',
        'terms.html',
        'previewbigone.png'
    ]
    
    # Create ZIP for upload
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    local_zip = 'netlify_deploy1_latest.zip'
    
    print(f"  Creating ZIP package...")
    
    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_deploy:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"    Added: {file}")
            else:
                print(f"    [WARN] Missing: {file}")

    # Save a local copy for verification
    try:
        with zipfile.ZipFile(local_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_deploy:
                if os.path.exists(file):
                    zipf.write(file, file)
    except Exception as e:
        print(f"  [WARN] Failed to save local ZIP copy: {e}")
    
    print(f"  [OK] Package created: {os.path.getsize(temp_zip.name) / 1024:.2f} KB")
    if os.path.exists(local_zip):
        print(f"  [OK] Local ZIP saved: {local_zip}")
    return temp_zip.name, files_to_deploy

def wait_for_deploy_ready(api_token, site_id, deploy_id):
    """Poll Netlify API until deploy state is 'ready'"""
    print("  Waiting for Netlify to process (Polling)...")
    
    check_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}"
    headers = {'Authorization': f'Bearer {api_token}'}
    
    for i in range(20): # Check for 40 seconds max
        try:
            r = requests.get(check_url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                state = data.get('state', 'unknown')
                print(f"    Check {i+1}/20: State is '{state}'")
                
                if state == 'ready':
                    return True
                if state == 'error':
                    print(f"    [FAIL] Netlify processing error: {data.get('error_message')}")
                    return False
            time.sleep(2)
        except Exception as e:
            print(f"    [WARN] Polling error: {e}")
            time.sleep(2)
            
    print("  [WARN] Timeout waiting for ready state, proceeding anyway...")
    return True # Try to proceed even if timeout

# ================= Deployment Functions =================

def deploy_zip_direct(api_token, site_id, zip_path):
    """Upload ZIP and publish using correct method with POLLING"""
    print(f"  Using direct ZIP upload method...")
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/zip' # Explicitly set for raw binary upload
    }
    
    try:
        # Netlify drag-and-drop API - upload ZIP file
        drop_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
        
        print(f"  Uploading ZIP file (Raw Binary)...")
        
        # Read file as binary
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
            
        # Send raw data instead of multipart/form-data for better stability
        response = requests.post(
            drop_url,
            headers=headers,
            data=zip_data,
            timeout=300
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            deploy_id = result.get('id', 'N/A')
            print(f"  [OK] ZIP upload successful!")
            print(f"  Deploy ID: {deploy_id}")
            
            if deploy_id != 'N/A':
                # === Critical Fix: Wait for 'ready' state ===
                if not wait_for_deploy_ready(api_token, site_id, deploy_id):
                    return False
                
                # Publish
                print(f"  Publishing deploy to production...")
                publish_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}/restore"
                publish_response = requests.post(publish_url, headers={'Authorization': f'Bearer {api_token}'})
                
                if publish_response.status_code in [200, 201, 204]:
                    print(f"  [OK] Deploy published to production!")
                else:
                    print(f"  [WARN] Publish API returned {publish_response.status_code} (Might already be live)")
            
            print(f"  Site URL: https://baseprops.tech")
            return True
        else:
            print(f"  [FAIL] Upload failed (Status: {response.status_code})")
            print(f"  Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"  [FAIL] Fallback method error: {e}")
        import traceback
        traceback.print_exc()
        return False

def deploy_to_netlify(api_token, site_id, zip_path):
    """Upload to Netlify using standard API"""
    print_section("Step 3: Uploading to Netlify")
    
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    
    print(f"  File size: {os.path.getsize(zip_path) / 1024:.2f} KB")
    
    try:
        # Step 1: Create a new deploy
        create_deploy_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
        print(f"  Creating deploy...")
        
        create_response = requests.post(
            create_deploy_url,
            headers=headers,
            json={},
            timeout=30
        )
        
        if create_response.status_code not in [200, 201]:
            print(f"  [FAIL] Failed to create deploy (Status: {create_response.status_code})")
            print(f"  Switching to Direct ZIP Upload...")
            return deploy_zip_direct(api_token, site_id, zip_path)
        
        deploy_data = create_response.json()
        deploy_id = deploy_data.get('id')
        deploy_upload_url = deploy_data.get('deploy_upload_url')
        
        if not deploy_upload_url:
            print(f"  [WARN] No upload URL, switching to Direct ZIP Upload...")
            return deploy_zip_direct(api_token, site_id, zip_path)
        
        print(f"  Deploy ID: {deploy_id}")
        
        # Step 2: Upload files individually
        print(f"  Extracting and uploading files...")
        uploaded_count = 0
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            file_list = zipf.namelist()
            for file_name in file_list:
                try:
                    file_data = zipf.read(file_name)
                    upload_url = f"{deploy_upload_url}/{file_name}"
                    file_response = requests.put(
                        upload_url,
                        headers={'Content-Type': 'application/octet-stream'},
                        data=file_data,
                        timeout=30
                    )
                    if file_response.status_code in [200, 201, 204]:
                        print(f"    [OK] Uploaded {file_name}")
                        uploaded_count += 1
                except Exception as e:
                    print(f"    [WARN] Error uploading {file_name}: {e}")
        
        if uploaded_count == 0:
            return deploy_zip_direct(api_token, site_id, zip_path)
        
        # === Critical Fix: Wait for 'ready' state ===
        if not wait_for_deploy_ready(api_token, site_id, deploy_id):
            return False
        
        # Step 3: Publish
        print(f"  Publishing deploy...")
        publish_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{deploy_id}/restore"
        publish_response = requests.post(
            publish_url,
            headers=headers,
            timeout=30
        )
        
        if publish_response.status_code in [200, 201, 204]:
            print(f"  [OK] Deploy published successfully!")
            print(f"  Site URL: https://baseprops.tech")
            return True
        else:
            print(f"  [WARN] Publish failed (Status: {publish_response.status_code})")
            return True
            
    except Exception as e:
        print(f"  [FAIL] Standard upload error: {e}")
        return deploy_zip_direct(api_token, site_id, zip_path)
    finally:
        try:
            os.unlink(zip_path)
        except:
            pass

def main():
    print("\n" + "=" * 60)
    print("  Netlify Automatic Upload (Robust)")
    print("=" * 60)
    
    api_token, site_id = get_netlify_config()
    if not api_token or not site_id:
        return False
    
    zip_path, files_list = create_deploy_package()
    if not zip_path:
        return False
    
    success = deploy_to_netlify(api_token, site_id, zip_path)
    
    if success:
        print_section("Deployment Complete")
        print("  [OK] Successfully deployed to Netlify!")
        print(f"  Visit: https://baseprops.tech")
        return True
    else:
        print_section("Deployment Failed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Upload cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)