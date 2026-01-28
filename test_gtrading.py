"""
Test GTrading with Playwright - detailed
"""
from playwright.sync_api import sync_playwright

print('=== GTrading Website Data (Playwright) ===')
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.gtrading.com.au/live-rate', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(3000)
    
    # Get all text length
    all_text = page.inner_text('body')
    print('Body text length:', len(all_text))
    
    # Check if page has rate data
    print('\nContains AUD:', 'AUD' in all_text)
    print('Contains CNY:', 'CNY' in all_text)
    print('Contains 澳元:', '澳元' in all_text)
    print('Contains 现汇:', '现汇' in all_text)
    
    # Find numbers that look like exchange rates (4.xxxx)
    import re
    numbers = re.findall(r'\d+\.\d{4}', all_text)
    print('\nExchange rate like numbers:', numbers[:10])
    
    # Find AUD/CNY related rows
    lines = all_text.split('\n')
    for line in lines:
        if 'AUD' in line and 'CNY' in line:
            print('AUD/CNY line:', line[:100])
    
    browser.close()
