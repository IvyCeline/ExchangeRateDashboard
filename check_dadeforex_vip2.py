import requests
import json

json_url = 'https://www.dadeforex.com/ratelist.json'
resp = requests.get(json_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
data = resp.json()
items = data.get('data', {}).get('results_rate_json') or data.get('results_rate_json') or []

# Find AUD/CNY entries
results = []
for item in items:
    pair = item.get('CurrencyPair')
    if isinstance(pair, dict):
        pair = pair.get('#text', '')
    if '澳元' in pair and '人民币' in pair:
        results.append({
            'CurrencyPair': pair,
            'VIPPrice': str(item.get('VIPPrice')),
            'VIPPrice_type': str(type(item.get('VIPPrice'))),
            'Ask': item.get('Ask'),
            'Bid': item.get('Bid')
        })

with open('dadeforex_vip_info.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('Saved to dadeforex_vip_info.json')

