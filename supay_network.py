from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        requests = []

        def on_request(req):
            if 'admin-ajax.php' in req.url or 'ajax' in req.url or req.resource_type == 'xhr':
                try:
                    post_data = req.post_data
                except:
                    post_data = None
                requests.append({'url': req.url, 'method': req.method, 'post_data': post_data})

        def on_response(resp):
            if 'admin-ajax.php' in resp.url or 'ajax' in resp.url or resp.request.resource_type == 'xhr':
                try:
                    text = resp.text()
                except:
                    text = '<no text>'
                requests.append({'url': resp.url, 'status': resp.status, 'response': text[:2000]})

        page.on('request', on_request)
        page.on('response', on_response)
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)
        browser.close()

    with open('supay_network.json', 'w', encoding='utf-8') as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)
    print('Saved supay_network.json with', len(requests), 'entries')

if __name__ == '__main__':
    main()









