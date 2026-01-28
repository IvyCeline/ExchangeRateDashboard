import requests
import json

json_url = 'https://www.dadeforex.com/ratelist.json'
resp = requests.get(json_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
data = resp.json()
items = data.get('data', {}).get('results_rate_json') or data.get('results_rate_json') or []

print('All CurrencyPairs:')
for item in items:
    pair = item.get('CurrencyPair')
    if isinstance(pair, dict):
        pair = pair.get('#text', '')
    print(f'  {pair}')

