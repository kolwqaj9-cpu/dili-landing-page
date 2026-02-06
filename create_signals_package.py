import os
import zipfile
import datetime

def create_signals_package():
    print("=" * 60)
    print("  创建 Signals 单版本部署包")
    print("=" * 60)

    files_to_deploy = [
        'index.html',              # 主页（原 signals_landing.html）
        'checkout.html',           # 下单页面
        'signals_dashboard.html',  # Dashboard
        'privacy.html',            # 隐私政策
        'terms.html',              # 服务条款
        'netlify.toml'             # Netlify 配置
    ]

    # 检查文件是否存在
    print("\n[检查] 检查文件是否存在...")
    print("-" * 60)
    for file in files_to_deploy:
        if os.path.exists(file):
            print(f"  [OK] {file.ljust(25)} ({os.path.getsize(file):>8} bytes)")
        else:
            print(f"  [FAIL] {file.ljust(25)} (文件未找到)")
            return None

    # 验证关键文件内容
    print("\n[验证] 验证关键文件内容...")
    print("-" * 60)
    
    # 检查 index.html 是否有 checkout 跳转
    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()
        if 'checkout.html' in index_content and 'Get Today\'s Picks' in index_content:
            print("  [OK] index.html - 包含下单流程")
        else:
            print("  [WARN] index.html - 下单流程可能不完整")
    
    # 检查 checkout.html 是否有免费试用逻辑
    with open('checkout.html', 'r', encoding='utf-8') as f:
        checkout_content = f.read()
        if 'Free Trial' in checkout_content and 'startAnalysis' in checkout_content:
            print("  [OK] checkout.html - 包含免费试用逻辑")
        else:
            print("  [WARN] checkout.html - 免费试用逻辑可能不完整")
    
    # 检查 signals_dashboard.html 是否有 API 调用
    with open('signals_dashboard.html', 'r', encoding='utf-8') as f:
        dashboard_content = f.read()
        if 'api.propkitai.tech' in dashboard_content or 'S_URL' in dashboard_content:
            print("  [OK] signals_dashboard.html - 包含数据获取逻辑")
        else:
            print("  [WARN] signals_dashboard.html - 数据获取逻辑可能不完整")

    # 创建ZIP包
    print("\n[打包] 创建 ZIP 包...")
    print("-" * 60)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"signals_only_{timestamp}.zip"

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_deploy:
            zipf.write(file, file)
            print(f"  [OK] 添加文件: {file}")

    print("\n" + "=" * 60)
    print("  打包完成!")
    print("=" * 60)

    print(f"\n  文件名称: {zip_filename}")
    print(f"  文件大小: {os.path.getsize(zip_filename)} bytes ({os.path.getsize(zip_filename) / 1024:.2f} KB)")
    print(f"  文件位置: {os.getcwd()}\\{zip_filename}")

    print("\n  包含页面:")
    print("  [OK] index.html - 主页（带下单按钮）")
    print("  [OK] checkout.html - 专业下单页面（显示免费试用）")
    print("  [OK] signals_dashboard.html - Dashboard（显示计算结果）")
    print("  [OK] privacy.html - 隐私政策")
    print("  [OK] terms.html - 服务条款")

    print("\n  用户流程:")
    print("  1. 访问 index.html → 输入邮箱 → 点击 'Get Today's Picks'")
    print("  2. 跳转到 checkout.html → 显示 $99/月 → 点击 'Complete Order'")
    print("  3. 弹出免费试用提示 → 点击 'Start Analysis Now'")
    print("  4. 触发 GPU 计算 → 跳转到 signals_dashboard.html")
    print("  5. Dashboard 显示计算结果（黄色背景 = 真实数据）")

    print("\n  下一步:")
    print("  1. 访问 https://app.netlify.com")
    print("  2. 选择站点: propkitai.tech")
    print("  3. 拖拽 ZIP 文件到部署区域")
    print("  4. 等待部署完成")
    print("  5. 点击 'Publish deploy' 按钮")

    print("\n  测试建议:")
    print("  1. 访问 https://propkitai.tech")
    print("  2. 输入测试邮箱")
    print("  3. 观察是否跳转到下单页面")
    print("  4. 点击下单后是否显示免费试用")
    print("  5. 确认是否触发 GPU 计算")

    return zip_filename

if __name__ == "__main__":
    create_signals_package()
