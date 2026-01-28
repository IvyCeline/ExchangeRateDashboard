"""
Save GTrading table HTML
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.gtrading.com.au/live-rate', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # Get table outerHTML
    table_html = page.evaluate('document.querySelector("table").outerHTML')
    
    # Save to file
    with open('gtrading_table.html', 'w', encoding='utf-8') as f:
        f.write(table_html)
    print('Saved to gtrading_table.html')
    
    browser.close()






