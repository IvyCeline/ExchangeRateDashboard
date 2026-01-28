"""
Check Dadeforex website directly with Playwright - using domcontentloaded
"""
from playwright.sync_api import sync_playwright

url = 'https://www.dadeforex.com/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(8000)
    
    # Find the AUD/CNY row data
    result = page.evaluate("""
        () => {
            const allText = document.body.innerText;
            const lines = allText.split('\\n');
            
            // Look for lines with AUD/CNY and numbers
            for (let line of lines) {
                if ((line.includes('澳元') && line.includes('人民币')) || 
                    (line.includes('AUD') && line.includes('CNY'))) {
                    
                    const numbers = line.match(/4\\.\\d{4}/g);
                    if (numbers && numbers.length >= 2) {
                        return {
                            line: line.trim(),
                            numbers: numbers
                        };
                    }
                }
            }
            return null;
        }
    """)
    
    print('Website result:', result)
    browser.close()

