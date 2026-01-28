"""
Deep debug Kundaxpay - 查找动态加载的数据
"""
from playwright.sync_api import sync_playwright
import json

url = 'https://www.kundaxpay.com.au/#/realTimeCurrency'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=60000)
    
    # Wait longer for dynamic content
    page.wait_for_timeout(10000)
    
    # Check console errors
    console_errors = []
    def handle_console(msg):
        if msg.type == 'error':
            console_errors.append(msg.text)
    
    page.on('console', handle_console)
    
    # Try different selectors
    result = page.evaluate("""
        () => {
            // Method 1: Find by Vue component or specific class
            const allElements = document.querySelectorAll('*');
            let audCnyData = [];
            
            for (let el of allElements) {
                const text = el.innerText || '';
                if (text.includes('AUD') && text.includes('CNY')) {
                    audCnyData.push({
                        tag: el.tagName,
                        class: el.className,
                        text: text.substring(0, 100)
                    });
                }
            }
            
            // Method 2: Check for tables with numbers
            let tables = [];
            document.querySelectorAll('table, .el-table, .ant-table').forEach(t => {
                tables.push({
                    class: t.className,
                    rows: t.querySelectorAll('tr').length
                });
            });
            
            // Method 3: Look for numbers in specific range (4.0-6.0 for AUD/CNY)
            let rateNumbers = [];
            const text = document.body.innerText;
            const regex = /4\\.\\d{4}/g;
            const matches = text.match(regex);
            if (matches) {
                rateNumbers = [...new Set(matches)];
            }
            
            return {
                audCnyElements: audCnyData.slice(0, 3),
                tables: tables,
                rateNumbers: rateNumbers,
                bodyText: text.substring(0, 500)
            };
        }
    """)
    
    print('Console errors:', console_errors)
    print('Result:', json.dumps(result, indent=2, ensure_ascii=False))
    browser.close()

