import streamlit as st
import os
import json
from bs4 import BeautifulSoup

# 配置页面为宽屏布局
st.set_page_config(layout="wide", page_title="QA Dashboard")

# 定义相关路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STRUCTURED_DIR = os.path.join(BASE_DIR, "structured_json")
APPROVED_DIR = os.path.join(BASE_DIR, "approved_json")
XML_DIR = os.path.join(BASE_DIR, "pmc_case_reports")

# 确保目标文件夹存在
os.makedirs(STRUCTURED_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)

st.title("👨‍⚕️ 医学生 QA 质检控制台")

# 扫描 structured_json 文件夹里所有待审核的 JSON 文件
json_files = [f for f in os.listdir(STRUCTURED_DIR) if f.endswith(".json")]

if not json_files:
    st.info("🎉 当前没有待审核的任务，等待 AI 提取...")
else:
    # 左侧边栏 (sidebar) 生成一个下拉菜单
    st.sidebar.header("任务列表")
    selected_file = st.sidebar.selectbox("选择要质检的文件", json_files)
    
    if selected_file:
        json_path = os.path.join(STRUCTURED_DIR, selected_file)
        xml_filename = selected_file.replace(".json", ".xml")
        xml_path = os.path.join(XML_DIR, xml_filename)
        
        # 加载待审核的 JSON 数据
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            st.error(f"无法读取 JSON 文件: {e}")
            data = {}
            
        age = data.get("patient_age", "")
        gender = data.get("patient_gender", "")
        drug = data.get("suspected_drug", "")
        labs = data.get("lab_results", {})
        outcome = data.get("clinical_outcome", "")
        score = data.get("AI_confidence_score", 0.0)
        
        # 左右分栏展示 (双栏对比)
        col1, col2 = st.columns(2)
        
        # 左栏：读取 XML 原始文本
        with col1:
            st.subheader("📄 原始病历文本")
            if os.path.exists(xml_path):
                with open(xml_path, "r", encoding="utf-8") as f:
                    xml_content = f.read()
                soup = BeautifulSoup(xml_content, "xml")
                
                abstract = soup.find("abstract")
                body = soup.find("body")
                
                abstract_text = abstract.get_text(separator="\n", strip=True) if abstract else ""
                body_text = body.get_text(separator="\n", strip=True) if body else ""
                
                full_text = f"【Abstract】\n{abstract_text}\n\n【Body】\n{body_text}"
            else:
                full_text = "⚠️ 未找到对应的原始 XML 文件。"
                
            # 文本展示在高度为 600 的 text_area 中（只读）
            st.text_area("原文对照", full_text, height=600, disabled=True, label_visibility="collapsed")
            
        # 右栏：JSON 字段编辑
        with col2:
            st.subheader("✍️ 提取字段校对")
            
            # 顶部高亮显示 AI_confidence_score
            try:
                score_val = float(score)
            except:
                score_val = 0.0
                
            if score_val < 0.6:
                st.error(f"⚠️ AI 提取置信度 (AI_confidence_score): {score} - 置信度较低，请仔细人工核对！")
            else:
                st.success(f"✅ AI 提取置信度 (AI_confidence_score): {score} - 置信度良好")
                
            # 可编辑的输入框
            with st.form(key="qa_form"):
                new_age = st.text_input("年龄 (patient_age)", value=str(age))
                new_gender = st.text_input("性别 (patient_gender)", value=str(gender))
                new_drug = st.text_input("疑似药物 (suspected_drug)", value=str(drug))
                
                if isinstance(labs, dict):
                    labs_str = json.dumps(labs, ensure_ascii=False, indent=2)
                else:
                    labs_str = str(labs)
                new_labs = st.text_area("化验指标 (lab_results)", value=labs_str, height=150)
                
                new_outcome = st.text_input("临床结局 (clinical_outcome)", value=str(outcome))
                
                # 确认并保存按钮
                submit_button = st.form_submit_button("✅ 确认无误并保存 (Approve)", type="primary")
                
                if submit_button:
                    try:
                        # 尝试将 lab_results 转回字典结构
                        parsed_labs = new_labs
                        try:
                            parsed_labs = json.loads(new_labs)
                        except:
                            pass
                            
                        approved_data = {
                            "patient_age": new_age,
                            "patient_gender": new_gender,
                            "suspected_drug": new_drug,
                            "lab_results": parsed_labs,
                            "clinical_outcome": new_outcome,
                            "AI_confidence_score": score,
                            "QA_status": "Approved"
                        }
                        
                        # 保存到 approved_json 文件夹中
                        approved_path = os.path.join(APPROVED_DIR, selected_file)
                        with open(approved_path, "w", encoding="utf-8") as f:
                            json.dump(approved_data, f, ensure_ascii=False, indent=4)
                            
                        # 自动删除原 structured_json 中的源文件
                        os.remove(json_path)
                        
                        st.success("🎉 数据已批准并保存！任务完成减一！")
                        # 刷新页面以进入下一个任务
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"保存时发生错误: {e}")
