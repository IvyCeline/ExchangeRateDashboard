from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'

def main():
    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1500)

        # collect script contents
        scripts = page.query_selector_all('script')
        script_texts = []
        for s in scripts:
            try:
                txt = s.inner_text()
            except Exception:
                txt = ''
            script_texts.append(txt)

        # find window properties that mention price/get_prices/stm
        props = page.evaluate("""() => {
            const keys = Object.getOwnPropertyNames(window);
            return keys.filter(k => /price|prices|get_prices|stm|ajaxurl/i.test(k)).slice(0,200);
        }""")

        out['window_props'] = props
        out['script_count'] = len(script_texts)
        out['scripts_search'] = []
        for i,txt in enumerate(script_texts):
            if not txt:
                continue
            low = txt.lower()
            if 'stm_get_prices' in low or 'get_prices' in low or 'admin-ajax' in low or 'ajaxurl' in low:
                snippet = txt[:2000]
                out['scripts_search'].append({'index': i, 'snippet': snippet})

        # also capture any network XHRs during initial load
        # reload capturing requests
        reqs = []
        def on_request(req):
            if req.resource_type == 'xhr' or 'admin-ajax' in req.url or 'ajax' in req.url:
                reqs.append({'url': req.url, 'method': req.method, 'post_data': req.post_data})
        page.on('request', on_request)
        page.reload(wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1000)
        out['xhr_requests'] = reqs

        browser.close()

    with open('supay_inspect.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Wrote supay_inspect.json')

if __name__ == '__main__':
    main()









