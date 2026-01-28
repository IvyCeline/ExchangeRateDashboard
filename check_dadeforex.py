"""
Check Dadeforex with Playwright
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.dadeforex.com/', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # Get page content
    tables = page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('table')).map(t => ({
                rows: Array.from(t.querySelectorAll('tr')).slice(0, 5).map(tr => {
                    return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim());
                })
            }));
        }
    """)
    
    print('Tables:', len(tables))
    for t in tables[:2]:
        print('Table:', t)
    
    # Find AUD/CNY data
    all_text = page.inner_text('body')
    print('Contains AUD:', 'AUD' in all_text)
    print('Contains CNY:', 'CNY' in all_text)
    
    # Find rate-like numbers
    import re
    numbers = re.findall(r'4\.\d{4}', all_text)
    print('Rate numbers:', numbers[:10])
    
    browser.close()






