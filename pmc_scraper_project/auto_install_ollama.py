import os
import sys
import io
import subprocess
import requests
from tqdm import tqdm

def auto_install():
    print("开始准备下载 Ollama...")
    url = "https://ollama.com/download/OllamaSetup.exe"
    installer_path = os.path.join(os.getcwd(), "OllamaSetup.exe")
    
    # 关键：配置本地代理以防断网
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }

    print(f"正在从 {url} 下载...")
    try:
        # 使用 stream=True 进行流式下载
        response = requests.get(url, stream=True, proxies=proxies, timeout=30)
        response.raise_for_status()
        
        # 获取文件总大小
        total_size = int(response.headers.get('content-length', 0))
        
        # 使用 tqdm 打印真实的进度条
        with open(installer_path, "wb") as file, tqdm(
            desc="OllamaSetup.exe",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            ascii=True # 为了终端兼容性，使用 ascii 字符
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
                
        print(f"\n下载成功，文件已保存至: {installer_path}")
    except Exception as e:
        print(f"下载失败: {e}")
        return

    print("\n开始执行无人化静默安装 (请耐心等待一两分钟)...")
    try:
        subprocess.run([installer_path, "/S"], check=True)
        print("安装程序已成功执行完闭！")
    except subprocess.CalledProcessError as e:
        print(f"执行安装包失败 (返回码 {e.returncode})")
    except Exception as e:
        print(f"执行安装时出现异常: {e}")

if __name__ == "__main__":
    # 解决终端输出中文乱码，并且不缓冲方便显示进度条
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    auto_install()