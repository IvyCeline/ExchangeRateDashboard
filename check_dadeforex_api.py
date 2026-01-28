"""
Check Dadeforex API response
"""
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.dadeforex.com/', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # Check the JSON API for latest data
    print('=== Checking JSON API ===')
    api_response = page.evaluate("""
        async () => {
            try {
                const resp = await fetch('https://www.dadeforex.com/ratelist.json');
                const data = await resp.json();
                return JSON.stringify(data).substring(0, 3000);
            } catch (e) {
                return 'Error: ' + e.toString();
            }
        }
    """)
    print('API response:', api_response)
    
    browser.close()






