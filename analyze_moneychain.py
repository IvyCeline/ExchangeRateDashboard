import requests
from bs4 import BeautifulSoup
import re
import sys
import io

# ensure utf-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://www.moneychain.com.au/exchange-rates/'
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers, timeout=15)
res.raise_for_status()
soup = BeautifulSoup(res.content, 'html.parser')

print('TITLE:', soup.title.string if soup.title else '')

# find blocks containing both 澳元 and 人民币
blocks = []
for tag in soup.find_all(['div','section','table','ul','p','span','td']):
    txt = tag.get_text(separator=' ', strip=True)
    if '澳元' in txt and '人民币' in txt:
        blocks.append((tag.name, tag.get('class'), txt))

print('\\nFound', len(blocks), 'blocks containing 澳元 and 人民币')
for i,(name,cls,txt) in enumerate(blocks[:6],1):
    print('\\n--- block', i, 'tag=', name, 'class=', cls)
    print(txt[:1000])

# table rows
for table in soup.find_all('table'):
    for row in table.find_all('tr'):
        cells = [c.get_text(strip=True) for c in row.find_all(['td','th'])]
        if any('澳元' in c or '人民币' in c for c in cells):
            print('\\nTable row:', cells)

# search numeric patterns in scripts
script_texts = '\\n'.join(s.get_text() for s in soup.find_all('script'))
nums = re.findall(r'\\d+\\.\\d{3,5}', script_texts)
print('\\nFound numeric patterns in scripts (sample):', nums[:20])

# plain numeric strings in page
num_elems = []
for s in soup.stripped_strings:
    if re.match(r'^\\d+\\.\\d{3,5}$', s):
        num_elems.append(s)

print('\\nFound', len(num_elems), 'plain numeric strings (sample):', num_elems[:20])










