import requests
from bs4 import BeautifulSoup
import re
import sys
import io

# 设置编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_supay():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        url = 'https://www.supay.com/en/'
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        print("=== SUPAY ANALYSIS ===")
        print(f"Status: {response.status_code}")

        # 查找汇率相关内容
        page_text = soup.get_text()
        print("\n--- 汇率相关文本 ---")
        lines = page_text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['rate', '汇率', 'aud', 'cny', '人民币', '澳元']):
                print(f"Line {i}: {line.strip()}")

        # 查找表格
        print("\n--- 表格 ---")
        tables = soup.find_all('table')
        print(f"找到 {len(tables)} 个表格")

        # 查找脚本
        print("\n--- 脚本分析 ---")
        scripts = soup.find_all('script')
        for i, script in enumerate(scripts):
            script_text = script.get_text() if script.get_text() else ''
            if len(script_text) > 100:  # 只分析较长的脚本
                if any(keyword in script_text.lower() for keyword in ['rate', '汇率', 'aud', 'cny']):
                    print(f"脚本 {i} 包含汇率相关内容，长度: {len(script_text)}")
                    # 显示前500个字符
                    print(script_text[:500] + "..." if len(script_text) > 500 else script_text)

        # 查找API调用
        print("\n--- 可能的API调用 ---")
        for script in scripts:
            script_text = script.get_text() if script.get_text() else ''
            # 查找fetch或XMLHttpRequest
            if 'fetch(' in script_text or 'XMLHttpRequest' in script_text or 'axios' in script_text:
                print("找到可能的API调用:")
                lines = script_text.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['fetch', 'xmlhttprequest', 'axios', 'api', 'rate']):
                        print(f"  {line.strip()}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_supay()
