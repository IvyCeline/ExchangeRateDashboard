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
                if (t.indexOf('澳元') !== -1 || /\\bAUD\\b/i.test(t)) {
                    // collect numbers in this element, its parent, and next 3 siblings
                    const nums = [];
                    const re = /\\d+\\.\\d{1,5}/g;
                    let m;
                    while ((m = re.exec(t)) !== null) nums.push(m[0]);
                    // parent
                    const parent = el.parentElement;
                    if (parent) {
                        const pt = (parent.innerText||'').trim();
                        while ((m = re.exec(pt)) !== null) nums.push(m[0]);
                    }
                    // next siblings
                    let sib = el.nextElementSibling;
                    let steps = 0;
                    while (sib && steps < 5) {
                        const st = (sib.innerText||'').trim();
                        while ((m = re.exec(st)) !== null) nums.push(m[0]);
                        sib = sib.nextElementSibling; steps++;
                    }
                    if (nums.length) {
                        out.push({text: t.slice(0,200), numbers: nums.slice(0,10)});
                    }
                }
            }
            return out.slice(0,40);
        }""")
        for i,r in enumerate(results):
            print('---',i)
            print(r['text'])
            print('numbers:', r['numbers'])
        browser.close()

if __name__ == '__main__':
    main()









