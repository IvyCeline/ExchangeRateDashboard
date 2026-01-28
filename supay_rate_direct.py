"""
直接访问 Supay iframe URL
"""
from playwright.sync_api import sync_playwright
import json

# 直接访问 iframe URL
url = 'https://www.supay.com/rate.php?lang=en'

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        print('Loading iframe URL directly...')
        page.goto(url, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)
        
        # 获取所有文本
        all_text = page.evaluate('() => document.body.innerText')
        print('All text preview:', all_text[:1000])
        
        # 查找表格
        tables = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll("table")).map((table, idx) => {
                    return {
                        index: idx,
                        headers: Array.from(table.querySelectorAll("th")).map(th => th.innerText.trim()),
                        rows: Array.from(table.querySelectorAll("tr")).slice(0, 10).map(tr => {
                            return Array.from(tr.querySelectorAll("td, th")).map(td => td.innerText.trim());
                        })
                    };
                });
            }
        """)
        print('Tables:', json.dumps(tables, indent=2, ensure_ascii=False))
        
        browser.close()

if __name__ == '__main__':
    main()






