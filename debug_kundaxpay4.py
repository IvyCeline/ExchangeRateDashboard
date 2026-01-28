"""
Find exact AUD/CNY row in Kundaxpay
"""
from playwright.sync_api import sync_playwright

url = 'https://www.kundaxpay.com.au/#/realTimeCurrency'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(10000)
    
    # Find the exact AUD/CNY row
    result = page.evaluate("""
        () => {
            const rows = document.querySelectorAll('tr, .el-table__row, [role="row"]');
            for (let row of rows) {
                const text = row.innerText || '';
                // Look for AUD CNY in the same row
                if ((text.includes('AUD') || text.includes('CNY')) && 
                    (text.includes('AUD') && text.includes('CNY'))) {
                    
                    // Extract all 4-digit numbers that look like rates
                    const numbers = text.match(/4\\.\\d{4}/g);
                    if (numbers && numbers.length >= 2) {
                        return {
                            success: true,
                            rowText: text.trim(),
                            numbers: numbers,
                            // Last two should be 现汇买入/卖出价
                            buy: numbers[numbers.length - 2],
                            sell: numbers[numbers.length - 1]
                        };
                    }
                }
            }
            
            // Fallback: Find any row with AUD and CNY text
            const allText = document.body.innerText;
            const lines = allText.split('\\n');
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                if (line.includes('AUD') && line.includes('CNY')) {
                    const nextFew = lines.slice(i, i+5).join(' | ');
                    const numbers = nextFew.match(/4\\.\\d{4}/g);
                    return {
                        context: nextFew,
                        numbers: numbers
                    };
                }
            }
            
            return {success: false};
        }
    """)
    
    print('Result:', result)
    browser.close()

