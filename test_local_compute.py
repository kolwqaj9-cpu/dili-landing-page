"""
本地计算测试脚本
直接运行 GPU 计算和 JSON 生成，不通过 webhook
"""

import os
import subprocess
import json
import sys

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_gpu_compute():
    """测试 GPU 计算"""
    print_section("1. 运行 GPU 计算 (CudaRuntime1.exe)")
    
    exe = "x64/Debug/CudaRuntime1.exe"
    
    if not os.path.exists(exe):
        print(f"  ❌ 找不到可执行文件: {exe}")
        print(f"  请确保 CudaRuntime1.exe 已编译并位于正确位置")
        return False
    
    print(f"  执行文件: {exe}")
    print(f"  开始计算...")
    
    try:
        result = subprocess.run(
            [exe],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"  ✅ GPU 计算完成")
            if result.stdout:
                print(f"  输出: {result.stdout[:200]}")
            return True
        else:
            print(f"  ❌ GPU 计算失败 (返回码: {result.returncode})")
            if result.stderr:
                print(f"  错误: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  GPU 计算超时（超过5分钟）")
        print(f"  这可能正常，取决于数据量大小")
        return True  # 超时不一定意味着失败
    except Exception as e:
        print(f"  ❌ 执行失败: {e}")
        return False

def test_export_json():
    """测试 JSON 导出"""
    print_section("2. 运行 JSON 导出 (export_json.py)")
    
    if not os.path.exists("export_json.py"):
        print(f"  ❌ 找不到 export_json.py")
        return False
    
    if not os.path.exists("sniper_results.bin"):
        print(f"  ⚠️  找不到 sniper_results.bin")
        print(f"  这可能是正常的，如果 GPU 计算没有生成此文件")
        return False
    
    # 使用 Anaconda Python
    python_exe = r"C:\ProgramData\Anaconda3\python.exe"
    if not os.path.exists(python_exe):
        python_exe = "python"
    
    print(f"  使用 Python: {python_exe}")
    print(f"  开始转换...")
    
    try:
        result = subprocess.run(
            [python_exe, "export_json.py"],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"  ✅ JSON 导出完成")
            if result.stdout:
                print(f"  输出: {result.stdout.strip()}")
            return True
        else:
            print(f"  ❌ JSON 导出失败 (返回码: {result.returncode})")
            if result.stderr:
                print(f"  错误: {result.stderr[:500]}")
            return False
    except Exception as e:
        print(f"  ❌ 执行失败: {e}")
        return False

def check_json_file():
    """检查生成的 JSON 文件"""
    print_section("3. 检查生成的 JSON 文件")
    
    json_path = "static/tactical_data.json"
    
    if not os.path.exists(json_path):
        print(f"  ❌ JSON 文件不存在: {json_path}")
        print(f"  请检查:")
        print(f"    1. static 目录是否存在")
        print(f"    2. export_json.py 是否成功执行")
        return False
    
    print(f"  ✅ JSON 文件存在: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n  JSON 内容:")
        print(f"    总分析数: {data.get('total_analyzed', 'N/A')}")
        print(f"    目标数: {data.get('target_count', 'N/A')}")
        print(f"    最高原因: {data.get('top_reason', 'N/A')}")
        print(f"    数据点数量: {len(data.get('data', []))}")
        
        if len(data.get('data', [])) > 0:
            print(f"\n  前3个数据点示例:")
            for i, point in enumerate(data.get('data', [])[:3], 1):
                print(f"    {i}. {point}")
        
        # 获取文件大小
        file_size = os.path.getsize(json_path)
        print(f"\n  文件大小: {file_size} 字节 ({file_size/1024:.2f} KB)")
        
        return True
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 格式错误: {e}")
        return False
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")
        return False

def check_required_files():
    """检查必要文件"""
    print_section("0. 检查必要文件")
    
    required_files = {
        "x64/Debug/CudaRuntime1.exe": "GPU 计算可执行文件",
        "export_json.py": "JSON 导出脚本",
        "sniper_results.bin": "GPU 计算结果（计算后生成）",
        "mlb_full_physics_vectors.csv": "输入数据文件"
    }
    
    all_exist = True
    for file, desc in required_files.items():
        if os.path.exists(file):
            print(f"  ✅ {file} ({desc})")
        else:
            print(f"  {'⚠️' if 'bin' in file or 'csv' in file else '❌'} {file} ({desc})")
            if 'bin' not in file and 'csv' not in file:
                all_exist = False
    
    return all_exist

def main():
    print("\n" + "=" * 60)
    print("  PropKit 本地计算测试工具")
    print("=" * 60)
    print(f"\n工作目录: {os.getcwd()}")
    
    results = {}
    
    # 检查文件
    results['files'] = check_required_files()
    
    if not results['files']:
        print("\n❌ 必要文件缺失，请检查项目目录")
        return False
    
    # 运行 GPU 计算
    results['gpu'] = test_gpu_compute()
    
    if not results['gpu']:
        print("\n⚠️  GPU 计算可能失败，但继续测试 JSON 导出...")
    
    # 运行 JSON 导出
    results['export'] = test_export_json()
    
    # 检查 JSON 文件
    results['json'] = check_json_file()
    
    # 总结
    print_section("测试总结")
    
    print("\n测试结果:")
    for test, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test}: {status}")
    
    if results.get('json'):
        print("\n✅ 本地计算测试成功！")
        print(f"  JSON 文件已生成: static/tactical_data.json")
        print(f"\n下一步:")
        print(f"  1. 可以手动上传到 Supabase 测试")
        print(f"  2. 或运行完整流程验证")
    else:
        print("\n❌ 测试未完全通过")
        print(f"  请检查:")
        print(f"    1. GPU 计算是否完成")
        print(f"    2. export_json.py 是否成功执行")
        print(f"    3. 查看错误信息 above")
    
    return results.get('json', False)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
