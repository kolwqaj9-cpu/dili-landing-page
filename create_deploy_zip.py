"""
Create ZIP package for Netlify deployment
All files ready for drag-and-drop upload
"""

import os
import zipfile
from datetime import datetime

def create_deploy_zip():
    """Create ZIP package with all deployment files"""
    
    # Files to include in deployment
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
    
    # Output ZIP file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"netlify_deploy_{timestamp}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)
    
    print("=" * 60)
    print("  Creating Netlify Deployment Package")
    print("=" * 60)
    print(f"\nOutput file: {zip_filename}")
    print(f"Location: {os.path.dirname(zip_path)}")
    print("\nFiles to include:")
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        added_count = 0
        missing_count = 0
        
        for file in files_to_deploy:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"  [OK] {file}")
                added_count += 1
            else:
                print(f"  [WARN] Missing: {file}")
                missing_count += 1
    
    # Get file size
    file_size_kb = os.path.getsize(zip_path) / 1024
    
    print("\n" + "=" * 60)
    print("  Package Created Successfully!")
    print("=" * 60)
    print(f"\n  File: {zip_filename}")
    print(f"  Size: {file_size_kb:.2f} KB")
    print(f"  Files added: {added_count}")
    if missing_count > 0:
        print(f"  Files missing: {missing_count}")
    
    print("\n  Next steps:")
    print("  1. Go to: https://app.netlify.com")
    print("  2. Drag and drop this ZIP file to your site")
    print("  3. Wait for deployment to complete")
    print("  4. Click 'Publish deploy' if needed")
    print(f"\n  ZIP file location:")
    print(f"  {zip_path}")
    
    return zip_path

if __name__ == "__main__":
    try:
        create_deploy_zip()
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
