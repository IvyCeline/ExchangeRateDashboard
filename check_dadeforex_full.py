import requests
import json

json_url = 'https://www.dadeforex.com/ratelist.json'
resp = requests.get(json_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
data = resp.json()
items = data.get('data', {}).get('results_rate_json') or data.get('results_rate_json') or []

# Get full details for both AUD/CNY entries
results = []
for item in items:
    pair = item.get('CurrencyPair')
    if isinstance(pair, dict):
        pair = pair.get('#text', '')
    if '澳元' in pair and '人民币' in pair:
        results.append({
            'CurrencyPair': pair,
            'VIPPrice': item.get('VIPPrice'),
            'Ask': item.get('Ask'),
            'Bid': item.get('Bid'),
            'AskCash': item.get('AskCash'),
            'BidCash': item.get('BidCash')
        })

# Save full details
with open('dadeforex_full.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('Saved full details to dadeforex_full.json')
print(f'Found {len(results)} AUD/CNY entries')

