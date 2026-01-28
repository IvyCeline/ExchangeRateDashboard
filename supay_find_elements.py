from playwright.sync_api import sync_playwright

URL = 'https://www.supay.com/en/'

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1500)

        results = page.evaluate("""() => {
            const out = [];
            const elems = Array.from(document.querySelectorAll('body *'));
            for (let el of elems) {
                const t = (el.innerText || '').trim();
                if (!t) continue;
                if (t.indexOf('澳元') !== -1 && t.indexOf('人民币') !== -1) {
                    out.push({tag: el.tagName, html: el.outerHTML.slice(0,1000), text: t.slice(0,400)});
                }
            }
            return out.slice(0,20);
        }""")
        for i,e in enumerate(results):
            print('--- element',i,'tag=',e['tag'])
            print(e['text'][:400])
            print(e['html'][:800])
            print('----')

        browser.close()

if __name__ == '__main__':
    main()









