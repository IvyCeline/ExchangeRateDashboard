from playwright.sync_api import sync_playwright

URL = 'https://www.moneychain.com.au/exchange-rates/'

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1500)
        sel_list = ['.header_currency', '.header_currency_swiper', '.content', '.rate-item', '.rate-list']
        out = {}
        for sel in sel_list:
            try:
                el = page.query_selector(sel)
                if el:
                    out[sel] = el.inner_text()[:1000]
            except Exception:
                out[sel] = None
        # also search for exact pair text
        pair_snippets = page.evaluate('''() => {
            const arr = [];
            const elems = Array.from(document.querySelectorAll('body *'));
            for (let el of elems) {
                const t = (el.innerText || '').trim();
                if (t.indexOf('澳元')!==-1 && t.indexOf('人民币')!==-1) {
                    arr.push(t.slice(0,400));
                }
            }
            return arr.slice(0,20);
        }''')
        out['pairs'] = pair_snippets
        browser.close()
    import json
    with open('moneychain_probe.json','w',encoding='utf-8') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
    print('Wrote moneychain_probe.json')

if __name__ == '__main__':
    main()


