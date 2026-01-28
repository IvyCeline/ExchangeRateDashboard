import requests
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from bs4 import BeautifulSoup
import re

url = 'https://www.moneychain.com.au/exchange-rates/'
res = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
res.raise_for_status()
soup = BeautifulSoup(res.content, 'html.parser')
page_text = soup.get_text(separator='\\n')
print('--- snippet containing 澳元 and 人民币 ---')
idx = page_text.find('澳元')
print(page_text[idx:idx+200])

pos = page_text.find('人民币')
print('\\n--- after 人民币 repr snippet ---')
print(repr(page_text[pos:pos+200]))

pattern = re.compile(r'澳元[\\s\\S]{0,200}?人民币[\\s\\S]{0,200}?(\\d+\\.\\d{3,5})')
m = pattern.search(page_text)
print('regex match:', bool(m))
if m:
    print('group1:', m.group(1))


