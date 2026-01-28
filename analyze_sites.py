import requests
from bs4 import BeautifulSoup
import json
import sys
import io

# 设置编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_website(url, name):
    """分析网站结构"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        print(f"\n=== {name.upper()} ===")
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")

        # 查找可能的汇率相关元素
        print("\n--- 查找汇率相关文本 ---")
        page_text = soup.get_text()
        lines = page_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['aud', 'cny', '人民币', '澳元', '汇率', 'rate', 'exchange']):
                print(f"Line {i}: {line}")

        # 查找表格
        print("\n--- 查找表格 ---")
        tables = soup.find_all('table')
        print(f"找到 {len(tables)} 个表格")

        for i, table in enumerate(tables):
            print(f"\n表格 {i+1}:")
            rows = table.find_all('tr')
            for row in rows[:5]:  # 只显示前5行
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text().strip() for cell in cells]
                print(f"  {cell_texts}")

        # 查找特定的div或span元素
        print("\n--- 查找汇率相关元素 ---")
        rate_elements = soup.find_all(['div', 'span', 'p'], class_=lambda c: c and any(keyword in c.lower() for keyword in ['rate', 'exchange', 'currency', 'price']))
        print(f"找到 {len(rate_elements)} 个可能的汇率元素")
        for elem in rate_elements[:10]:  # 只显示前10个
            print(f"  {elem.name} class='{elem.get('class')}' text='{elem.get_text().strip()}'")

        # 查找包含数字的元素（可能是汇率）
        print("\n--- 查找包含数字的元素 ---")
        import re
        number_pattern = re.compile(r'\d+\.\d+')
        number_elements = soup.find_all(text=number_pattern)
        print(f"找到 {len(number_elements)} 个包含数字的文本")
        for elem in number_elements[:20]:  # 只显示前20个
            print(f"  '{elem.strip()}'")

    except Exception as e:
        print(f"Error analyzing {name}: {e}")

if __name__ == "__main__":
    sites = {
        'supay': 'https://www.supay.com/en/',
        'moneychase': 'https://www.moneychase.com.au/currency-rate-page/',
        'dadeforex': 'https://www.dadeforex.com/',
        'gtrading': 'https://www.gtrading.com.au/live-rate',
        'kundaxpay': 'https://www.kundaxpay.com.au/#/realTimeCurrency'
    }

    for name, url in sites.items():
        analyze_website(url, name)
