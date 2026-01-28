import requests
import re
import sys
import io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def inspect(url):
    print('\\n===', url, '===')
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = [s.get_text() for s in soup.find_all('script') if s.get_text()]
    combined = '\\n'.join(scripts)
    full = r.text
    matches = []
    # find admin-ajax usage
    for m in re.finditer(r'admin-ajax\\.php', full):
        start = max(0, m.start()-200)
        end = m.end()+200
        snippet = full[start:end]
        matches.append(snippet)
    print('admin-ajax occurrences:', len(matches))
    for i,s in enumerate(matches[:10],1):
        print('\\n--- snippet', i, '---')
        print(s[:800])

    # search for ajax action names
    actions = set(re.findall(r"action\\s*[:=]\\s*['\\\"]([a-zA-Z0-9_\\-]+)['\\\"]", combined))
    print('\\nFound actions:', actions)

    # search for fetch/XHR calls with urls
    xhrs = re.findall(r'(fetch\\([^)]*\\))|(axios\\.post\\([^)]*\\))|(\\$\\.post\\([^)]*\\))', combined)
    for x in xhrs[:10]:
        print('\\nXHR candidate:', ''.join(x)[:400])

if __name__ == '__main__':
    sites = [
        'https://www.supay.com/en/',
        'https://www.moneychase.com.au/currency-rate-page/',
    ]
    for s in sites:
        try:
            inspect(s)
        except Exception as e:
            print('error for', s, e)


