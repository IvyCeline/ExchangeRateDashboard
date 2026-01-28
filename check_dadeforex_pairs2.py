import requests
import json

json_url = 'https://www.dadeforex.com/ratelist.json'
resp = requests.get(json_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
data = resp.json()
items = data.get('data', {}).get('results_rate_json') or data.get('results_rate_json') or []

pairs_info = []
for item in items:
    pair = item.get('CurrencyPair')
    if isinstance(pair, dict):
        pair = pair.get('#text', '')
    pairs_info.append(pair)

with open('pairs_info.txt', 'w', encoding='utf-8') as f:
    json.dump(pairs_info, f, ensure_ascii=False, indent=2)

print('Saved to pairs_info.txt')

