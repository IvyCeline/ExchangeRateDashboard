"""
Supay 页面结构深度分析
"""
from playwright.sync_api import sync_playwright
import json
import re

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
        page.wait_for_timeout(5000)
        
        # 查找 Real Time Exchange Rate 附近的元素
        near_heading = page.evaluate("""
            () => {
                const elements = [];
                const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                
                for (let h of headings) {
                    if (h.innerText.includes('Real Time') || h.innerText.includes('Exchange Rate')) {
                        // 获取父容器
                        let parent = h.parentElement;
                        for (let i = 0; i < 5 && parent; i++) {
                            elements.push({
                                tag: parent.tagName,
                                class: parent.className,
                                id: parent.id,
                                innerHTML: parent.innerHTML.substring(0, 300)
                            });
                            parent = parent.parentElement;
                        }
                        break;
                    }
                }
                
                return elements;
            }
        """)
        result['near_heading'] = near_heading
        
        # 查找所有包含 VIP 的元素
        vip_elements = page.evaluate("""
            () => {
                const elements = [];
                const all = document.querySelectorAll('*');
                
                for (let el of all) {
                    const text = (el.innerText || '').trim();
                    if (text.toLowerCase() === 'vip' || text.toLowerCase().includes('vip ')) {
                        elements.push({
                            tag: el.tagName,
                            class: el.className,
                            id: el.id,
                            text: text,
                            parentTag: el.parentElement?.tagName,
                            parentClass: el.parentElement?.className,
                            html: el.outerHTML.substring(0, 200)
                        });
                    }
                }
                
                return elements;
            }
        """)
        result['vip_elements'] = vip_elements
        
        # 查找包含 AUD CNY 的元素
        aud_cny_elements = page.evaluate("""
            () => {
                const elements = [];
                const all = document.querySelectorAll('*');
                
                for (let el of all) {
                    const text = (el.innerText || '').trim();
                    if ((text.includes('AUD') || text.includes('澳元')) && 
                        (text.includes('CNY') || text.includes('人民币'))) {
                        if (text.length < 200) {
                            elements.push({
                                tag: el.tagName,
                                class: el.className,
                                text: text.substring(0, 150)
                            });
                        }
                    }
                }
                
                return elements.slice(0, 10);
            }
        """)
        result['aud_cny_elements'] = aud_cny_elements
        
        # 查找所有包含 4.xxxx 格式价格的元素
        price_elements = page.evaluate("""
            () => {
                const elements = [];
                const all = document.querySelectorAll('*');
                
                for (let el of all) {
                    const text = (el.innerText || '').trim();
                    if (/^4\\.\\d{4}$/.test(text)) {
                        // 获取完整上下文
                        let fullContext = '';
                        let parent = el;
                        for (let i = 0; i < 3; i++) {
                            if (!parent) break;
                            fullContext = parent.outerHTML || '';
                            if (fullContext.length > 50) break;
                            parent = parent.parentElement;
                        }
                        
                        elements.push({
                            tag: el.tagName,
                            class: el.className,
                            text: text,
                            context: fullContext.substring(0, 300)
                        });
                    }
                }
                
                return elements;
            }
        """)
        result['price_elements'] = price_elements
        
        # 检查是否有 iframe
        iframes = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('iframe')).map(f => ({
                    src: f.src,
                    name: f.name,
                    id: f.id
                }));
            }
        """)
        result['iframes'] = iframes
        
        browser.close()
    
    # 保存结果
    with open('supay_structure.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n=== RESULT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()






