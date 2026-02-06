"""
打包所有 HTML 文件到 ZIP
"""

import os
import zipfile
from datetime import datetime

def package_html_files():
    """打包所有 HTML 文件"""
    
    # 查找所有 HTML 文件
    html_files = []
    for file in os.listdir('.'):
        if file.endswith('.html') and os.path.isfile(file):
            html_files.append(file)
    
    if not html_files:
        print("未找到 HTML 文件")
        return None
    
    # 按字母顺序排序
    html_files.sort()
    
    # 创建 ZIP 文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"html_files_{timestamp}.zip"
    
    print("=" * 60)
    print("  打包 HTML 文件")
    print("=" * 60)
    print(f"\n找到 {len(html_files)} 个 HTML 文件：")
    
    # 创建 ZIP 文件
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for html_file in html_files:
            zipf.write(html_file, html_file)
            file_size = os.path.getsize(html_file)
            print(f"  [OK] {html_file:30s} ({file_size:>8,} bytes)")
    
    # 获取 ZIP 文件大小
    zip_size = os.path.getsize(zip_filename)
    
    print("\n" + "=" * 60)
    print("  打包完成")
    print("=" * 60)
    print(f"\n  文件名: {zip_filename}")
    print(f"  文件大小: {zip_size:,} bytes ({zip_size/1024:.2f} KB)")
    print(f"  包含文件: {len(html_files)} 个")
    print(f"  文件位置: {os.path.abspath(zip_filename)}")
    
    return zip_filename

if __name__ == "__main__":
    try:
        zip_file = package_html_files()
        if zip_file:
            print(f"\n✅ 成功创建 ZIP 文件: {zip_file}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
