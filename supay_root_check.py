from playwright.sync_api import sync_playwright
import json

URLS = ['https://www.supay.com/en/','https://www.supay.com/']

def check():
    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for url in URLS:
            page = browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            txt = page.evaluate("() => document.body.innerText.slice(0,2000)")
            out[url] = {'len': len(txt), 'snippet': txt}
            page.close()
        browser.close()
    with open('supay_root_check.json','w',encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Wrote supay_root_check.json')

if __name__ == '__main__':
    check()









