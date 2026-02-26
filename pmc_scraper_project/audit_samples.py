import os
import sys
import io
import json
from bs4 import BeautifulSoup
from openai import OpenAI

# 解决终端输出中文乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.join(base_dir, "structured_json")
    xml_dir = os.path.join(base_dir, "pmc_case_reports")
    
    if not os.path.exists(json_dir):
        print(f"找不到文件夹: {json_dir}")
        return

    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    if not json_files:
        print("未找到任何待审计的 JSON 文件。")
        return

    # 设置 DeepSeek API 客户端
    client = OpenAI(
        base_url="https://api.deepseek.com",
        api_key="sk-23eb9ad719954686b14e33f01f8e766e"
    )
    
    system_prompt = """
你是一位严谨的医学数据质检员。
我将提供给你一份原始的病历文本（XML提取内容）和一份 AI 生成的结构化 JSON 数据。
请你对这份 JSON 数据的质量进行审计打分。

打分维度（满分10分）：
1. 准确性（0-4分）：JSON 里的指标（ALT/AST/Bilirubin等）与原文是否严丝合缝一致，绝无捏造或串位？
2. 推断力（0-3分）：对于 suspected_drug（疑似致病药物）的判定是否符合文本语境和临床常识？
3. 完整性（0-3分）：有没有遗漏原文中明确提到的关键结局（clinical_outcome，如出院、换肝、死亡）？

请强制以严格合法的 JSON 对象输出结果，必须包含以下两个字段：
- "total_score": 总得分（0到10的整数或浮点数）
- "deduction_reason": 失分原因（如果满分10分，请填 "完美，无失分"；如果有扣分，请用简短的1-2句话说明到底错在哪、漏了啥）
"""

    print("="*60)
    print(f"{'文件名':<20} | {'得分':<5} | {'失分原因'}")
    print("-" * 60)

    for json_filename in json_files[:5]: # 限制前5个
        json_path = os.path.join(json_dir, json_filename)
        xml_filename = json_filename.replace('.json', '.xml')
        xml_path = os.path.join(xml_dir, xml_filename)
        
        # 1. 读取 JSON 数据
        try:
            with open(json_path, 'r', encoding='utf-8') as jf:
                extracted_data = jf.read()
        except Exception:
            continue
            
        # 2. 读取原始 XML 文本
        try:
            with open(xml_path, 'r', encoding='utf-8') as xf:
                xml_content = xf.read()
            soup = BeautifulSoup(xml_content, 'xml')
            abstract_text = soup.find('abstract').get_text(separator=' ', strip=True) if soup.find('abstract') else ""
            body_text = soup.find('body').get_text(separator=' ', strip=True) if soup.find('body') else ""
            full_text = f"{abstract_text}\n\n{body_text}".strip()[:5000] # 控制长度防止超窗
        except Exception:
            full_text = "未找到对应的原始文本。"

        # 3. 构造请求内容
        user_prompt = f"【原始病历文本】\n{full_text}\n\n【AI提取的JSON数据】\n{extracted_data}"
        
        # 4. 调用 API 进行审计
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            audit_result_str = response.choices[0].message.content.strip()
            audit_result = json.loads(audit_result_str)
            
            score = audit_result.get("total_score", "N/A")
            reason = audit_result.get("deduction_reason", "未知")
            
            # 格式化输出
            file_disp = json_filename[:18] + ".." if len(json_filename)>20 else json_filename
            print(f"{file_disp:<20} | {str(score):<5} | {reason}")
            
        except Exception as e:
            print(f"{json_filename:<20} | ERROR | {e}")

    print("="*60)

if __name__ == "__main__":
    main()
