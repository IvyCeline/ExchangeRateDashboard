import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://www.supay.com/en/'
headers = {'User-Agent':'Mozilla/5.0'}

def main():
    r = requests.get(BASE, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = soup.find_all('script', src=True)
    print('Found', len(scripts), 'external scripts')
    for s in scripts:
        src = s['src']
        full = urljoin(BASE, src)
        try:
            rr = requests.get(full, headers=headers, timeout=10)
            if rr.status_code==200:
                text = rr.text
                if 'stm_get_prices' in text or 'get_prices' in text or 'admin-ajax' in text:\n+                    print('\\n--', full)\n+                    # print small snippet around keyword\n+                    idx = text.find('stm_get_prices')\n+                    if idx!=-1:\n+                        print(text[max(0,idx-200):idx+200])\n+                    else:\n+                        idx = text.find('get_prices')\n+                        if idx!=-1:\n+                            print(text[max(0,idx-200):idx+200])\n+        except Exception as e:\n+            print('err fetching', full, e)\n+\n+if __name__=='__main__':\n+    main()\n+

