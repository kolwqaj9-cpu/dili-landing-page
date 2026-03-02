import os
import sys
import io
import time
import requests
from bs4 import BeautifulSoup

# 解决终端输出中文乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

# 请修改为您的真实邮箱地址，以符合 NCBI API 的使用规范
EMAIL = "dummy_email@example.com"

# 代理设置，如果不需要可以注释掉
PROXIES = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "pmc_case_reports")
    os.makedirs(output_dir, exist_ok=True)
    
    print("开始搜索 PubMed Central...")
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pmc",
        "term": '("drug-induced liver injury" OR "DILI") AND "case reports"[Filter] AND "humans"[Filter] AND open access[filter]',
        "retmode": "json",
        "retmax": 100,
        "email": EMAIL
    }
    
    try:
        response = requests.get(search_url, params=search_params, proxies=PROXIES)
        response.raise_for_status()
        search_data = response.json()
        
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        print(f"搜索完成，共找到 {len(id_list)} 篇文献。")
    except Exception as e:
        print(f"搜索失败: {e}")
        return

    time.sleep(0.5)
    
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    
    batch_size = 50
    for i in range(0, len(id_list), batch_size):
        batch_ids = id_list[i:i+batch_size]
        print(f"正在下载第 {i//batch_size + 1} 批，共 {len(batch_ids)} 篇文献...")
        
        fetch_params = {
            "db": "pmc",
            "id": ",".join(batch_ids),
            "retmode": "xml",
            "email": EMAIL
        }
        
        try:
            fetch_res = requests.get(fetch_url, params=fetch_params, proxies=PROXIES)
            fetch_res.raise_for_status()
            
            # 解析 XML
            soup = BeautifulSoup(fetch_res.content, "xml")
            articles = soup.find_all("article")
            
            if not articles:
                print("本批次未找到 article 标签。开始打印返回内容前500字符供调试：")
                print(fetch_res.text[:500])
                continue

            for article in articles:
                pmc_id = None
                article_ids = article.find_all("article-id")
                
                for aid in article_ids:
                    if aid.get("pub-id-type") in ("pmc", "pmcid"):
                        pmc_id = aid.text.strip()
                        break
                
                # 有些文献可能没明确写 pub-id-type="pmc"，我们可以通过 pmc-id 标签或者直接拿取其它 ID
                if not pmc_id:
                    # 如果仍然没有，记录一下存在的 pub-id-type
                    types = [aid.get("pub-id-type") for aid in article_ids]
                    print(f"未能找到 pmc 类型的 ID。存在的类型有: {types}")
                    continue
                
                file_path = os.path.join(output_dir, f"PMC{pmc_id}.xml")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(article))
                print(f"已保存: PMC{pmc_id}.xml")
                    
        except Exception as e:
            print(f"获取全文批次时出错: {e}")
            
        time.sleep(0.5)

    print(f"\n所有抓取完成。文件已保存至：\n{output_dir}")

if __name__ == "__main__":
    main()
