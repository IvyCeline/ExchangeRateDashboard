"""
Check Kundaxpay actual data with Playwright
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.kundaxpay.com.au/#/realTimeCurrency', wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(5000)
    
    # Find table data
    result = page.evaluate("""
        () => {
            const rows = document.querySelectorAll('tr');
            for (let row of rows) {
                const text = row.innerText || '';
                if ((text.includes('AUD') || text.includes('澳元')) && 
                    (text.includes('CNY') || text.includes('人民币'))) {
                    const cells = Array.from(row.querySelectorAll('td')).map(td => td.innerText.trim());
                    return {
                        found: true,
                        cells: cells,
                        fullText: text
                    };
                }
            }
            return {found: false};
        }
    """)
    
    print('Kundaxpay result:', result)
    
    # Also check for any table structure
    tables = page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('table')).map((t, idx) => {
                return {
                    index: idx,
                    rows: Array.from(t.querySelectorAll('tr')).slice(0, 5).map(tr => {
                        return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim());
                    })
                };
            });
        }
    """)
    print('Tables:', tables)
    
    browser.close()






