"""
Test websites with Playwright
"""
from playwright.sync_api import sync_playwright
import json

def test_dadeforex():
    print('=== Dadeforex Website Data (Playwright) ===')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.dadeforex.com/', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(2000)
        
        # Get all text
        text = page.inner_text('body')
        print('Body text contains AUD/CNY:', 'AUD' in text and 'CNY' in text)
        
        # Find tables
        tables = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('table')).map((table, idx) => {
                    return {
                        index: idx,
                        rows: Array.from(table.querySelectorAll('tr')).slice(0, 5).map(tr => {
                            return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim());
                        })
                    };
                });
            }
        """)
        print(f'Tables found: {len(tables)}')
        for t in tables[:2]:
            print(f'Table {t["index"]}: {json.dumps(t["rows"], ensure_ascii=False)[:500]}')
        
        browser.close()

def test_gtrading():
    print('\n=== GTrading Website Data (Playwright) ===')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.gtrading.com.au/live-rate', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(2000)
        
        # Get all text
        text = page.inner_text('body')
        print('Body text contains AUD/CNY:', 'AUD' in text and 'CNY' in text)
        
        # Find tables
        tables = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('table')).map((table, idx) => {
                    const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
                    return {
                        index: idx,
                        headers: headers,
                        rows: Array.from(table.querySelectorAll('tr')).slice(0, 5).map(tr => {
                            return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim());
                        })
                    };
                });
            }
        """)
        print(f'Tables found: {len(tables)}')
        for t in tables[:2]:
            print(f'Table {t["index"]}: headers={t["headers"]}')
            print(f'  First rows: {json.dumps(t["rows"][:3], ensure_ascii=False)}')
        
        browser.close()

def test_kundaxpay():
    print('\n=== Kundaxpay Website Data (Playwright) ===')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.kundaxpay.com.au/#/realTimeCurrency', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)
        
        # Find tables
        tables = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('table')).map((table, idx) => {
                    return {
                        index: idx,
                        rows: Array.from(table.querySelectorAll('tr')).slice(0, 5).map(tr => {
                            return Array.from(tr.querySelectorAll('td, th')).map(td => td.innerText.trim());
                        })
                    };
                });
            }
        """)
        print(f'Tables found: {len(tables)}')
        for t in tables:
            print(f'Table {t["index"]}: {json.dumps(t["rows"], ensure_ascii=False)[:500]}')
        
        browser.close()

if __name__ == '__main__':
    test_dadeforex()
    test_gtrading()
    test_kundaxpay()






