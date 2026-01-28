"""
Save Dadeforex API response
"""
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.dadeforex.com/', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # Check the JSON API for latest data
    api_response = page.evaluate("""
        async () => {
            try {
                const resp = await fetch('https://www.dadeforex.com/ratelist.json');
                const data = await resp.json();
                return data;
            } catch (e) {
                return {error: e.toString()};
            }
        }
    """)
    
    # Save to file
    with open('dadeforex_api.json', 'w', encoding='utf-8') as f:
        json.dump(api_response, f, ensure_ascii=False, indent=2)
    print('Saved to dadeforex_api.json')
    
    browser.close()






