import os
import sys
import io
import json
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# 解决终端输出中文乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# 设置 OpenAI 客户端连接 DeepSeek 官方 API
client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key="sk-23eb9ad719954686b14e33f01f8e766e"
)

SYSTEM_PROMPT = """
You are a final quality assurance auditor for medical datasets.
Please check the provided JSON string for two criteria:
1. It MUST NOT contain any Chinese characters.
2. It MUST contain a specific numeric/measured value for either "ALT" or "AST" inside "lab_results" (i.e., not null, not empty, not just "elevated").
If BOTH criteria are met, output exactly and only "YES". Otherwise, output "NO".
"""

def deepseek_verify(json_str):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json_str}
            ],
            temperature=0.0
        )
        result = response.choices[0].message.content.strip()
        return result.upper() == "YES"
    except Exception as e:
        print(f"API Error during verification: {e}")
        return False

def process_file(json_path):
    filename = os.path.basename(json_path)
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        status = data.get("status")
        if status != "accepted":
            return None
            
        score = data.get("AI_confidence_score", 0.0)
        try:
            score = float(score)
        except:
            score = 0.0
            
        if score < 0.85:
            return None
            
        # Perform DeepSeek final check
        json_str = json.dumps(data, ensure_ascii=False)
        is_passed = deepseek_verify(json_str)
        
        if is_passed:
            return filename
        else:
            return None
            
    except Exception as e:
        return None

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(base_dir, "structured_json")
    xml_dir = os.path.join(base_dir, "pmc_case_reports")
    
    if not os.path.exists(json_dir):
        print("未找到 structured_json 目录，请先运行提取脚本。")
        return
        
    json_files = [os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.endswith('.json')]
    print(f"找到 {len(json_files)} 个 JSON 文件。开始最后一道 DeepSeek 质检...")
    
    passed_files = []
    
    # 使用线程池并发验证
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_file, fp): fp for fp in json_files}
        
        for future in as_completed(futures):
            res = future.result()
            if res:
                passed_files.append(res)
                print(f"✅ [通过] 极品数据: {res}")
                
    if not passed_files:
        print("\n很遗憾，没有找到符合所有苛刻条件（置信度>=0.85，无中文，含ALT/AST指标）的数据。")
        return
        
    print(f"\n质检完毕！共有 {len(passed_files)} 份数据脱颖而出。准备打包...")
    
    zip_filename = os.path.join(base_dir, "DILI_Golden_Samples_For_Review.zip")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for json_filename in passed_files:
            # 加入 JSON
            json_path = os.path.join(json_dir, json_filename)
            zipf.write(json_path, os.path.join("Structured_JSON", json_filename))
            
            # 加入对应 XML
            xml_filename = json_filename.replace('.json', '.xml')
            xml_path = os.path.join(xml_dir, xml_filename)
            if os.path.exists(xml_path):
                zipf.write(xml_path, os.path.join("Raw_XML", xml_filename))
                
    print(f"🎉 成功！已将 {len(passed_files)} 份极品数据打包完毕！")
    print(f"压缩包路径: {zip_filename}")

if __name__ == "__main__":
    main()
