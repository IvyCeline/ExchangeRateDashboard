from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'

def main():
    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)

        # search for labels commonly used for rates
        keywords = ['现汇买入', '现汇卖出', '现钞买入', '现钞卖出', '买入价', '卖出价', 'AUD', '澳元', '人民币', 'CNY']
        matches = []
        elems = page.query_selector_all('body *')
        for el in elems:
            try:
                t = el.inner_text().strip()
            except:
                t = ''
            if any(k in t for k in keywords):
                matches.append({'text': t[:500], 'html': el.inner_html()[:1000], 'tag': el.evaluate("e => e.tagName")})
        out['matches'] = matches[:200]
        browser.close()

    with open('supay_dom_inspect.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Wrote supay_dom_inspect.json')

if __name__ == '__main__':
    main()









