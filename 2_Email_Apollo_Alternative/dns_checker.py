import time
import subprocess

def check_dns():
    print("正在查询 dilisights.com 的 TXT 记录...")
    try:
        # 使用 nslookup 查询
        result = subprocess.run(["nslookup", "-q=txt", "dilisights.com"], capture_output=True, text=True, timeout=10)
        output = result.stdout
        
        if "TsH_6" in output:
            print("\n" + "="*50)
            print("🚀【检测成功】全球 DNS 已经更新！TXT 记录已生效！")
            print("目前检测到的记录如下：")
            for line in output.split('\n'):
                if "text =" in line or "google-site-verification" in line:
                    print("  ", line.strip())
            print("="*50 + "\n")
            print("请立即前往 Google Search Console 点击【验证】！")
            return True
        else:
            print(f"⏳ 暂未检测到 TsH_6 开头的验证记录。当前查询结果：\n{output}")
            print("60秒后重新查询...")
            return False
    except Exception as e:
        print(f"查询出错: {e}")
        return False

if __name__ == "__main__":
    while True:
        success = check_dns()
        if success:
            break
        time.sleep(60)
