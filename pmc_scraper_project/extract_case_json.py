import os
import sys
import io
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from openai import OpenAI

# 解决终端输出中文乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# 设置 OpenAI 客户端连接 DeepSeek 官方 API
client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key="sk-23eb9ad719954686b14e33f01f8e766e"
)
MODEL_NAME = "deepseek-chat"

SYSTEM_PROMPT = """
CRITICAL: All output (including chain_of_thought and data fields) MUST be in English only. Never use Chinese characters.

You are a top clinical pharmacologist. Your task is to extract information from medical case report texts and strictly output valid JSON format.

【Gatekeeper Rules】:
Before extracting, first determine the type of the literature.
If it is an animal experiment, a review, or not a specific human case report, output directly:
{
  "status": "rejected",
  "reason": "Not a human case report"
}

If it is a qualifying human Case Report, perform 【Deep Extraction】 and output a JSON object containing the following fields (if not mentioned in the original text, fill with null):
{
  "status": "accepted",
  "chain_of_thought": "[Article Type: Case Report] In this article, I found the following liver injury-related lab values and clinical outcomes: ...",
  "patient_age": "Age (number or string)",
  "patient_gender": "Must be exactly 'Male' or 'Female' (do not use other terms)",
  "suspected_drug": "Suspected drug causing liver injury",
  "lab_results": {
    "ALT": "Peak value and unit",
    "AST": "Peak value and unit",
    "ALP": "Peak value and unit",
    "GGT": "Peak value and unit",
    "Bilirubin": "Peak value and unit (including total/direct bilirubin)",
    "INR": "Peak value and unit",
    "Albumin": "Lowest value or abnormal value and unit"
  },
  "clinical_outcome": "Clinical outcome (Null is strictly prohibited. If improved/discharged is mentioned, must be 'Improved/Discharged'; if death, 'Death'; if liver transplant, 'Liver Transplantation', etc.)",
  "AI_confidence_score": Float between 0.0 and 1.0 evaluating the completeness and confidence of the extraction
}

Requirements:
1. Extraction perspective: Read the Case Presentation and Results sections carefully, finding all mentioned peak values of liver function indicators. Pay special attention to text within tables and figure legends to find specific peak values for ALT/AST.
2. English descriptions: Any text or description within lab_results MUST be in English.
3. Absolutely pure JSON: The entire output must be a valid JSON object without any Markdown tags (like ```json) or extra wrapping text.

CRITICAL: All output (including chain_of_thought and data fields) MUST be in English only. Never use Chinese characters.
"""

def process_file(filepath, output_dir):
    filename = os.path.basename(filepath)
    output_filename = filename.replace('.xml', '.json')
    output_filepath = os.path.join(output_dir, output_filename)
    
    # 为了演示，允许覆盖重写
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'xml')
        
        # 使用 BeautifulSoup 提取纯文本，洗掉所有 XML 标签
        abstract = soup.find('abstract')
        body = soup.find('body')
        
        abstract_text = abstract.get_text(separator=' ', strip=True) if abstract else ""
        body_text = body.get_text(separator=' ', strip=True) if body else ""
        
        full_text = f"{abstract_text}\n\n{body_text}".strip()
        
        if not full_text:
            return f"[{filename}] 警告：未找到正文，跳过。"
            
        # 扩大视野至 32000 字符
        sliced_text = full_text[:32000]
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"病历文本如下：\n{sliced_text}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        raw_response = response.choices[0].message.content.strip()
        extracted_data = json.loads(raw_response)
        
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
            
        status = extracted_data.get("status", "unknown")
        if status == "rejected":
            return f"[{filename}] 拒绝提取：{extracted_data.get('reason')}"
        else:
            return f"[{filename}] 成功提取，得分: {extracted_data.get('AI_confidence_score', 'N/A')}"
            
    except Exception as e:
        return f"[{filename}] 处理出错：{e}"

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "pmc_case_reports")
    output_dir = os.path.join(base_dir, "structured_json")
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_dir):
        print("未找到 pmc_case_reports 目录。")
        return
        
    xml_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.xml')]
    
    # 限制处理所有可用的文件
    print(f"找到 {len(xml_files)} 个 XML 文件。开始使用 DeepSeek 并发处理...")
    
    # 使用 ThreadPoolExecutor 并发处理，设置 max_workers=5 (避免触发API速率限制过快)
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_file, fp, output_dir): fp for fp in xml_files}
        
        for future in as_completed(futures):
            print(future.result())
            
    elapsed = time.time() - start_time
    print(f"\n全部处理完成！耗时: {elapsed:.2f} 秒。")

if __name__ == "__main__":
    main()
