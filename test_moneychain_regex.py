import requests\n+from bs4 import BeautifulSoup\n+import re\n+\n+url = 'https://www.moneychain.com.au/exchange-rates/'\n+res = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)\n+res.raise_for_status()\n+soup = BeautifulSoup(res.content, 'html.parser')\n+page_text = soup.get_text(separator='\\n')\n+print('--- snippet containing 澳元 and 人民币 ---')\n+idx = page_text.find('澳元')\n+print(page_text[idx:idx+200])\n+\n+pattern = re.compile(r'澳元[\\s\\S]{0,60}?人民币[\\s\\S]{0,10}?(\\d+\\.\\d{3,5})')\n+m = pattern.search(page_text)\n+print('regex match:', bool(m))\n+if m:\n+    print('group1:', m.group(1))\n+\n*** End Patch">









