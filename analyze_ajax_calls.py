import requests
import re
import sys
import io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HEADERS = {'User-Agent': 'Mozilla/5.0'}
SITES = {
    'supay': 'https://www.supay.com/en/',
    'moneychase': 'https://www.moneychase.com.au/currency-rate-page/'
}

def analyze_site(name, url):
    print(f'\\n=== {name} ({url}) ===')
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
    except Exception as e:
        print('fetch error', e)
        return
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    scripts = [s.get_text() for s in soup.find_all('script') if s.get_text()]
    combined = '\\n'.join(scripts) + '\\n' + html

    # Find admin-ajax usages and any AJAX URLs
    admin_ajax = re.findall(r'admin-ajax\\.php', combined, re.I)
    print('admin-ajax occurrences:', len(admin_ajax))

    # Find fetch/ajax urls
    urls = set()
    for m in re.finditer(r'["\\\'](https?:\\\\/\\\\/[^"\\\']+?)["\\\']', combined):
        urls.add(m.group(1).replace('\\\\/','/'))
    for u in list(urls)[:40]:
        print(' candidate URL:', u)

    # Heuristic: look for $.post or ajax calls to admin-ajax
    for s in scripts:
        if 'admin-ajax.php' in s or '.ajax' in s or 'fetch(' in s or 'XMLHttpRequest' in s or 'axios' in s:
            lines = s.split('\\n')
            for i,l in enumerate(lines):
                if 'admin-ajax.php' in l or '.ajax' in l or 'fetch(' in l or 'axios' in l:
                    context = '\\n'.join(lines[max(0,i-3):i+4])
                    print('\\n--- script snippet ---\\n', context[:1000])
                    break

if __name__ == '__main__':
    for name, url in SITES.items():
        analyze_site(name, url)









