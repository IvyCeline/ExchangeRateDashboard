"""
Supay 精确抓取 - 针对 VIP 行的 AUD/CNY 汇率
简化版本
"""
from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'

def main():
    result = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        )
        
        page = context.new_page()
        page.set_default_timeout(60000)
        
        print("Loading Supay page...")
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)
        
        # 获取页面 HTML 预览
        html_sample = page.evaluate("""
            () => {
                // 查找 Real Time Exchange Rate 标题
                const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                for (let h of headings) {
                    if (h.innerText.includes('Real Time') || h.innerText.includes('Exchange Rate')) {
                        return {
                            found: true,
                            heading: h.innerText.trim(),
                            parentHTML: h.parentElement.innerHTML.substring(0, 500)
                        };
                    }
                }
                return {found: false, availableHeadings: Array.from(headings).map(h => h.innerText.trim()).slice(0, 5)};
            }
        """)
        result['heading_search'] = html_sample
        
        # 查找表格
        tables_info = page.evaluate("""
            () => {
                const tables = document.querySelectorAll('table');
                return Array.from(tables).map((table, idx) => {
                    const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
                    const rows = Array.from(table.querySelectorAll('tr')).slice(0, 5).map(tr => {
                        return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim()).join(' | ');
                    });
                    return {index: idx, headers: headers, sampleRows: rows};
                });
            }
        """)
        result['tables'] = tables_info
        
        # 查找 VIP 行
        vip_row = page.evaluate("""
            () => {
                const rows = document.querySelectorAll('tr');
                for (let row of rows) {
                    const text = row.innerText || '';
                    if (text.toLowerCase().includes('vip') && text.includes('AUD') && text.includes('CNY')) {
                        const cells = Array.from(row.querySelectorAll('td, th')).map(td => td.innerText.trim());
                        return {found: true, cells: cells, fullText: text};
                    }
                }
                return {found: false};
            }
        """)
        result['vip_row'] = vip_row
        
        # 查找价格 4.6885 和 4.8625
        price_search = page.evaluate("""
            () => {
                const prices = [];
                const all = document.querySelectorAll('*');
                for (let el of all) {
                    const text = (el.innerText || '').trim();
                    if (/^4\\.\\d{4}$/.test(text)) {
                        // 找到上下文
                        let context = '';
                        let parent = el.parentElement;
                        for (let i = 0; i < 3 && parent; i++) {
                            context = parent.innerText || '';
                            if (context.includes('VIP') || context.includes('AUD')) break;
                            parent = parent.parentElement;
                        }
                        
                        prices.push({
                            value: text,
                            context: context.substring(0, 200)
                        });
                    }
                }
                return prices;
            }
        """)
        result['prices_found'] = price_search
        
        browser.close()
    
    # 保存结果
    with open('supay_vip_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n=== RESULT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
