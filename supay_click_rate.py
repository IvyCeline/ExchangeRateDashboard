from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'

def main():
    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1000)
        # try to click link with text 'Real Time' or '实时' or '实时汇率'
        clicked = None
        keywords = ['Real Time Exchange Rate','Real Time','实时汇率','实时']
        for txt in keywords:
            try:
                anchor = page.query_selector("text=\"" + txt + "\"")
                if anchor:
                    anchor.click()
                    page.wait_for_timeout(2000)
                    clicked = txt
                    break
            except Exception:
                continue
        out['clicked'] = clicked
        out['body_snippet'] = page.evaluate('() => document.body.innerText.slice(0,2000)')
        # capture XHRs after click
        reqs = []
        def on_request(req):
            if req.resource_type == 'xhr' or 'admin-ajax' in req.url or 'rate' in req.url:
                reqs.append({'url': req.url, 'method': req.method, 'post_data': req.post_data})
        page.on('request', on_request)
        page.wait_for_timeout(2000)
        out['requests_after'] = reqs
        browser.close()
    with open('supay_click_out.json','w',encoding='utf-8') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
    print('Wrote supay_click_out.json')

if __name__=='__main__':
    main()


