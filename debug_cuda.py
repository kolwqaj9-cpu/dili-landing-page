import os
import subprocess
import sys

def debug_engine():
    print("🕵️‍♂️ === CUDA 引擎侦探程序启动 ===\n")

    # 1. 寻找 .exe 文件
    # 常见的 Visual Studio 编译输出路径
    possible_paths = [
        "x64/Debug/CudaRuntime1.exe",
        "x64/Release/CudaRuntime1.exe",
        "CudaRuntime1.exe", # 有时会在根目录
        "Debug/CudaRuntime1.exe"
    ]
    
    found_exe = None
    for p in possible_paths:
        if os.path.exists(p):
            found_exe = p
            print(f"✅ 找到引擎文件: {os.path.abspath(p)}")
            break
    
    if not found_exe:
        print("❌ 致命错误：在所有常见路径下都找不到 CudaRuntime1.exe！")
        print("   -> 请检查 Visual Studio 是否编译成功？")
        print("   -> 请检查您的文件结构，main.py 是否和 x64 文件夹在同一级？")
        return

    # 2. 检查输入文件 (.bin)
    # C++ 程序需要读取 mlb_physics_full.bin，如果没有这个文件，它会直接报错退出
    bin_file = "mlb_physics_full.bin"
    if not os.path.exists(bin_file):
        print(f"\n❌ 致命错误：找不到输入文件 {bin_file}")
        print("   -> C++ 引擎需要这个文件才能跑。")
        print("   -> 请先运行一次 'python erjinzhi.py' 来生成这个文件！")
        return
    else:
        print(f"✅ 找到输入数据: {bin_file}")

    # 3. 尝试运行
    print(f"\n🚀 正在尝试运行: {found_exe} ...")
    print("--------------------------------------------------")
    
    try:
        # 显式捕获输出，让你看到 C++ 到底说了什么
        result = subprocess.run(
            [found_exe], 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=os.getcwd() # 强制在当前目录运行，确保日志生成在这里
        )
        
        print("C++ 标准输出 (STDOUT):")
        print(result.stdout)
        print("C++ 错误输出 (STDERR):")
        print(result.stderr)
        
    except subprocess.CalledProcessError as e:
        print("\n❌ 运行失败！(C++ 程序报错退出)")
        print(f"错误码: {e.returncode}")
        print("C++ 输出信息:")
        print(e.stdout)
        print(e.stderr)
    except Exception as e:
        print(f"\n❌ Python 调用出错: {e}")

    print("--------------------------------------------------")

    # 4. 检查日志
    if os.path.exists("cuda_activity.log"):
        print("\n✅ 成功检测到 'cuda_activity.log'！")
        print("   内容如下：")
        with open("cuda_activity.log", "r") as f:
            print(f"   {f.read()}")
    else:
        print("\n❌ 依然没有发现 'cuda_activity.log'。")
        print("   这说明 C++ 程序可能启动了，但在写日志之前就崩了，或者代码没更新。")

if __name__ == "__main__":
    debug_engine()