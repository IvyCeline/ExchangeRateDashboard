"""
Debug Kundaxpay - 查找正确的数据结构
"""
from playwright.sync_api import sync_playwright

url = 'https://www.kundaxpay.com.au/#/realTimeCurrency'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(5000)
    
    # Check for AUD/CNY data
    result = page.evaluate("""
        () => {
            const allText = document.body.innerText;
            const lines = allText.split('\\n');
            
            // Find lines with AUD and CNY
            for (let line of lines) {
                if (line.includes('AUD') && line.includes('CNY')) {
                    return {found: true, line: line.trim()};
                }
            }
            
            return {found: false, allTextLength: allText.length};
        }
    """)
    
    print('Result:', result)
    browser.close()

