"""
Supay 从 iframe 中提取 VIP 汇率数据
修正版本 - 使用正确的 Frame 对象方法
"""
from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'
IFRAME_SRC = 'https://www.supay.com/rate.php?lang=en'

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
        
        # 查找并进入 iframe
        print("Looking for iframe...")
        
        # 等待 iframe 加载
        page.wait_for_selector('iframe[src*="rate.php"]', timeout=10000)
        
        # 获取 iframe 的 frame 对象
        frame = page.frame('iframe[src*="rate.php"]')
        
        if frame:
            print("Found iframe, extracting data...")
            
            # 在 iframe 中查找所有文本
            iframe_content = frame.evaluate("""
                () => {
                    return {
                        allText: document.body.innerText,
                        tables: Array.from(document.querySelectorAll('table')).map((table, idx) => {
                            return {
                                index: idx,
                                headers: Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim()),
                                rows: Array.from(table.querySelectorAll('tr')).slice(0, 10).map(tr => {
                                    return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim());
                                })
                            };
                        })
                    };
                }
            """)
            
            result['iframe_content'] = iframe_content
            
            # 查找 VIP 行
            vip_row = frame.evaluate("""
                () => {
                    const rows = document.querySelectorAll('tr');
                    for (let row of rows) {
                        const text = row.innerText || '';
                        if (text.toLowerCase().includes('vip') && 
                            (text.includes('AUD') || text.includes('CNY'))) {
                            const cells = Array.from(row.querySelectorAll('td, th')).map(td => td.innerText.trim());
                            return {found: true, cells: cells, fullText: text};
                        }
                    }
                    return {found: false};
                }
            """)
            result['vip_row'] = vip_row
            
            # 查找价格 4.xxxx
            prices = frame.evaluate("""
                () => {
                    const prices = [];
                    const all = document.querySelectorAll('*');
                    
                    for (let el of all) {
                        const text = (el.innerText || '').trim();
                        if (/^4\\.\\d{4}$/.test(text)) {
                            // 查找父元素中的 VIP 和 AUD CNY
                            let parent = el.parentElement;
                            let context = '';
                            for (let i = 0; i < 5 && parent; i++) {
                                context = parent.innerText || '';
                                if (context.includes('VIP')) break;
                                parent = parent.parentElement;
                            }
                            
                            prices.push({
                                value: text,
                                hasVipContext: context.includes('VIP'),
                                contextPreview: context.substring(0, 100)
                            });
                        }
                    }
                    
                    return prices;
                }
            """)
            result['prices'] = prices
            
        else:
            result['error'] = 'Iframe not found'
        
        browser.close()
    
    # 保存结果
    with open('supay_iframe_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n=== RESULT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
