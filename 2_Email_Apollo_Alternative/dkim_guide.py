import webbrowser

def dkim_guide():
    print("="*60)
    print("🚀 Google Workspace DKIM 自动引导提取工具")
    print("="*60)
    print("\n【步骤 1】：请确保你已经以超级管理员身份登录了 Google Workspace 后台。")
    print("正在为你自动打开 Gmail 身份验证（DKIM）设置页面...")
    
    # 直接打开 DKIM 设置页面
    webbrowser.open("https://admin.google.com/ac/apps/gmail/authenticateemail")
    
    print("\n【步骤 2】：在打开的页面中操作：")
    print("  1. 在顶部的下拉菜单中，选择你的域名：dilisights.com")
    print("  2. 点击【生成新记录】(Generate new record)")
    print("  3. 选项保持默认即可（2048位, 前缀默认是 'google'）")
    print("  4. 点击【生成】")
    
    print("\n【步骤 3】：你会在页面上看到一个长长的字符串。")
    print("请手动将页面上的 TXT 记录值（以 v=DKIM1; k=rsa; p=... 开头的那段极长的代码）复制下来。")
    
    dkim_value = input("\n👉 请在此处粘贴你复制的 DKIM 记录值 (直接回车可跳过): ").strip()
    
    if dkim_value:
        print("\n✅ 提取成功！请前往【腾讯云 DNSPod】添加以下记录：")
        print("-" * 60)
        print("记录类型 (Type) : TXT")
        print("主机记录 (Name) : google._domainkey")
        print(f"记录值 (Value)  : {dkim_value}")
        print("-" * 60)
        print("⚠️ 注意：添加后可能需要 10-30 分钟生效。生效后，请记得在 Google 后台点击【开始身份验证 (Start Authentication)】。")
    else:
        print("\n如果你现在还没拿到，等拿到后按以下格式去腾讯云添加：")
        print("类型: TXT | 主机记录: google._domainkey | 记录值: 你复制的一大串代码")

if __name__ == "__main__":
    dkim_guide()
