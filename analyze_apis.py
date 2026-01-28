import requests
import re
import sys
import io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SITES = {
    'moneychain': 'https://www.moneychain.com.au/exchange-rates/',
    'supay': 'https://www.supay.com/en/',
    'moneychase': 'https://www.moneychase.com.au/currency-rate-page/',
    'dadeforex': 'https://www.dadeforex.com/',
    'gtrading': 'https://www.gtrading.com.au/live-rate',
    'kundaxpay': 'https://www.kundaxpay.com.au/#/realTimeCurrency'
}

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def find_candidates(text):
    urls = set()
    # common patterns for api/json endpoints
    for m in re.finditer(r'(https?:\/\/[^\s"\'\\]+?\.(?:json|php|ashx|aspx|svc)[^\s"\'\\]*)', text, re.I):
        urls.add(m.group(1))
    for m in re.finditer(r'(["\'])(\/[^\s"\'\\]+?(?:api|rate|json|get|data)[^\s"\'\\]+)\1', text, re.I):
        urls.add(m.group(2))
    for m in re.finditer(r'(fetch\(|axios\.get\(|XMLHttpRequest\(|\$.get\()', text):
        # capture nearby URL strings
        nearby = text[max(0, m.start()-200):m.end()+400]
        for u in re.findall(r'["\'](https?:\/\/[^\s"\'\\]+)["\']', nearby):
            urls.add(u)
    return list(urls)

def analyze(url):
    print('\\n===', url, '===')
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
    except Exception as e:
        print('fetch error:', e)
        return
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    scripts = ''.join([s.get_text() for s in soup.find_all('script') if s.get_text()])
    candidates = find_candidates(scripts + '\\n' + html)
    print('Found candidate endpoints:', len(candidates))
    for c in candidates[:20]:
        print('  ', c)

    # quick attempt to request candidate JSON endpoints
    for c in candidates:
        try:
            url_c = c
            if url_c.startswith('/'):
                # make absolute
                from urllib.parse import urljoin
                url_c = urljoin(url, url_c)
            rr = requests.get(url_c, headers=HEADERS, timeout=8)
            ctype = rr.headers.get('Content-Type','')
            if rr.status_code == 200 and ('json' in ctype or rr.text.strip().startswith('{') or rr.text.strip().startswith('[')):
                print('\\n--- JSON candidate OK ---')
                print(url_c)
                print('Content-Type:', ctype)
                txt = rr.text[:1000]
                print('Preview:', txt.replace('\\n',' ')[:800])
                # don't try too many
                break
        except Exception:
            continue

if __name__ == '__main__':
    for name, url in SITES.items():
        analyze(url)









