"""
Supay 高级抓取 - 使用真实浏览器配置和等待策略
"""
from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'

def main():
    result = {}
    with sync_playwright() as p:
        # 使用真实的浏览器配置
        browser = p.chromium.launch(
            headless=False,  # 先用有头模式看看
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
        )
        
        page = context.new_page()
        
        # 设置更长的超时
        page.set_default_timeout(60000)
        
        # 访问页面
        print("Loading page...")
        page.goto(URL, wait_until='domcontentloaded', timeout=30000)
        
        # 等待页面完全加载
        page.wait_for_load_state('networkidle')
        print("Page loaded, waiting for content...")
        
        # 额外等待让 JS 执行
        page.wait_for_timeout(5000)
        
        # 获取页面完整 HTML
        html = page.content()
        result['html_length'] = len(html)
        
        # 查找页面中的所有脚本和样式
        scripts = page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script')).map(s => ({
                    src: s.src,
                    innerText: s.innerText.substring(0, 200)
                })).filter(s => s.src || s.innerText);
                return scripts;
            }
        """)
        result['scripts'] = scripts[:5]  # 只返回前5个
        
        # 尝试查找价格表格
        page_prices = page.evaluate("""
            () => {
                const result = {tables: [], text_snippets: []};
                
                // 查找所有表格
                const tables = document.querySelectorAll('table');
                for (let i = 0; i < tables.length; i++) {
                    const table = tables[i];
                    const rows = [];
                    for (let tr of table.querySelectorAll('tr')) {
                        const cells = [];
                        for (let td of tr.querySelectorAll('td, th')) {
                            cells.push(td.innerText.trim());
                        }
                        if (cells.length > 0) rows.push(cells);
                    }
                    if (rows.length > 0) {
                        result.tables.push({
                            index: i,
                            rows: rows.slice(0, 10)  # 只返回前10行
                        });
                    }
                }
                
                // 查找包含 AUD/CNY 或澳元/人民币 的文本
                const allText = document.body.innerText;
                const lines = allText.split('\\n');
                for (let line of lines) {
                    if ((line.includes('AUD') || line.includes('澳元')) && 
                        (line.includes('CNY') || line.includes('人民币'))) {
                        result.text_snippets.push(line.trim());
                    }
                }
                
                return result;
            }
        """)
        result['page_prices'] = page_prices
        
        # 查找可能的汇率元素
        rate_elements = page.evaluate("""
            () => {
                const elements = [];
                
                // 查找包含 rate 或 汇率 的元素
                const all = document.querySelectorAll('*');
                for (let el of all) {
                    const text = el.innerText || '';
                    if ((text.includes('AUD') || text.includes('CNY')) && 
                        text.includes('Buy') || text.includes('Sell') ||
                        text.includes('买入') || text.includes('卖出')) {
                        if (text.length < 100 && text.length > 5) {
                            elements.push({
                                tag: el.tagName,
                                class: el.className,
                                text: text.trim()
                            });
                        }
                    }
                }
                
                return elements.slice(0, 20);
            }
        """)
        result['rate_elements'] = rate_elements
        
        # 查找可能的按钮或链接
        interactive_elements = page.evaluate("""
            () => {
                const elements = [];
                const all = document.querySelectorAll('button, a, [role="button"], [onclick]');
                for (let el of all) {
                    const text = el.innerText || el.textContent || '';
                    if (text.toLowerCase().includes('rate') || 
                        text.toLowerCase().includes('exchange') ||
                        text.includes('汇率')) {
                        elements.push({
                            tag: el.tagName,
                            class: el.className,
                            text: text.trim().substring(0, 50),
                            onclick: el.getAttribute('onclick')?.substring(0, 100)
                        });
                    }
                }
                return elements.slice(0, 10);
            }
        """)
        result['interactive_elements'] = interactive_elements
        
        browser.close()
    
    # 保存结果
    with open('supay_advanced.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to supay_advanced.json")
    print(f"HTML length: {result['html_length']}")
    print(f"Tables found: {len(result['page_prices']['tables'])}")
    print(f"Text snippets: {len(result['page_prices']['text_snippets'])}")
    print(f"Rate elements: {len(result['rate_elements'])}")

if __name__ == '__main__':
    main()






