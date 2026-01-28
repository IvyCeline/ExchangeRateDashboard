# -*- coding: utf-8 -*-
"""
深入检查 Dadeforex 网页结构
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright

print("=" * 60)
print("深入检查 Dadeforex 网页结构")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto("https://www.dadeforex.com/", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    # 检查页面中的表格
    print("\n1. 检查所有表格:")
    tables = page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('table')).map((table, idx) => {
                return {
                    index: idx,
                    className: table.className,
                    id: table.id,
                    rows: Array.from(table.querySelectorAll('tr')).slice(0, 3).map(tr => {
                        return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim().substring(0, 50));
                    })
                };
            });
        }
    """)

    for t in tables:
        print(f"\n表格 {t['index']}: class={t['className']}, id={t['id']}")
        for i, row in enumerate(t['rows'][:3]):
            print(f"  Row {i}: {row}")

    # 查找 AUD/CNY 相关内容
    print("\n2. 查找 AUD/CNY 相关内容:")
    aud_cny = page.evaluate("""
        () => {
            // 查找包含澳元和人民币的所有元素
            const results = [];
            const elements = document.querySelectorAll('*');
            
            for (let el of elements) {
                const text = el.innerText || '';
                if ((text.includes('AUD') || text.includes('澳元')) && 
                    (text.includes('CNY') || text.includes('人民币')) &&
                    text.length < 200) {  // 限制文本长度
                    
                    // 提取价格
                    const prices = text.match(/4\\.\\d{4}/g);
                    if (prices && prices.length >= 2) {
                        results.push({
                            tag: el.tagName,
                            class: el.className,
                            text: text.substring(0, 200),
                            prices: prices
                        });
                    }
                }
            }
            return results.slice(0, 10);  // 最多返回10个
        }
    """)

    for item in aud_cny:
        print(f"\n标签: {item['tag']}, class: {item['class']}")
        print(f"文本: {item['text'][:100]}...")
        print(f"价格: {item['prices']}")

    browser.close()
