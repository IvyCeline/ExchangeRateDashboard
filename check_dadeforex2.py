"""
Check Dadeforex page structure with Playwright
"""
from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.dadeforex.com/', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # Get all text
    all_text = page.inner_text('body')
    print('All text length:', len(all_text))
    print('Text preview:', all_text[:1000])
    
    # Check for AUD and CNY mentions
    print('\nContains 澳元:', '澳元' in all_text)
    print('Contains 人民币:', '人民币' in all_text)
    
    # Check for currency pairs
    print('\nAUD related lines:')
    lines = all_text.split('\n')
    for line in lines:
        if 'AUD' in line or '澳元' in line:
            print('  ', line[:100])
    
    # Check the JSON API for latest data
    print('\n=== Checking JSON API ===')
    api_response = page.evaluate("""
        async () => {
            try {
                const resp = await fetch('https://www.dadeforex.com/ratelist.json');
                const data = await resp.json();
                return JSON.stringify(data).substring(0, 2000);
            } catch (e) {
                return 'Error: ' + e.toString();
            }
        }
    """)
    print('API response:', api_response)
    
    browser.close()






