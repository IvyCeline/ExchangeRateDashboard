from playwright.sync_api import sync_playwright
import re

URL = 'https://www.kundaxpay.com.au/#/realTimeCurrency'

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1500)

        results = page.evaluate('''() => {
            const out = [];
            const elems = Array.from(document.querySelectorAll('body *'));
            for (let el of elems) {
                const t = (el.innerText||'').trim();
                if (!t) continue;
                // find numbers 4.x
                const nums = t.match(/\\d+\\.\\d{1,5}/g) || [];
                for (let n of nums) {
                    const v = parseFloat(n);
                    if (v>3.5 && v<6.5) {
                        // capture ancestor chain
                        let anc = el;
                        let chain = [];
                        for (let i=0;i<3 && anc;i++) {
                            chain.push(anc.tagName + ':' + (anc.className||'').toString().slice(0,100));
                            anc = anc.parentElement;
                        }
                        out.push({text: t.slice(0,200), num: n, chain: chain});
                        break;
                    }
                }
            }
            // dedupe by text
            const seen = new Set(); const res=[];
            for (let o of out) {
                if (!seen.has(o.text)) { seen.add(o.text); res.push(o); }
            }
            return res.slice(0,80);
        }''')
        # write results to file to avoid console encoding issues
        import json, io, sys
        with open('kundax_probe_out.json','w',encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print('Wrote kundax_probe_out.json with', len(results), 'entries')
        browser.close()

if __name__ == '__main__':
    main()


