"""
Deep debug Kundaxpay - simplified output
"""
from playwright.sync_api import sync_playwright

url = 'https://www.kundaxpay.com.au/#/realTimeCurrency'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=60000)
    
    # Wait longer for dynamic content
    page.wait_for_timeout(10000)
    
    # Look for rate numbers directly
    result = page.evaluate("""
        () => {
            const text = document.body.innerText;
            const regex = /4\\.\\d{4}/g;
            const matches = text.match(regex);
            return {
                found: matches && matches.length > 0,
                numbers: matches ? [...new Set(matches)] : [],
                hasAUD: text.includes('AUD'),
                hasCNY: text.includes('CNY')
            };
        }
    """)
    
    print('Result:', result)
    browser.close()

