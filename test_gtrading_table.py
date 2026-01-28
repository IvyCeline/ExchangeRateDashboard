"""
Test GTrading table HTML
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.gtrading.com.au/live-rate', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # 获取表格的 outerHTML
    table_html = page.evaluate('document.querySelector("table").outerHTML')
    print('Table HTML length:', len(table_html))
    print('Table HTML preview:', table_html[:1500])
    
    browser.close()






