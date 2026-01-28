import requests
import json

json_url = 'https://www.dadeforex.com/ratelist.json'
resp = requests.get(json_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
data = resp.json()
items = data.get('data', {}).get('results_rate_json') or data.get('results_rate_json') or []

# Find AUD/CNY entries
for item in items:
    pair = item.get('CurrencyPair')
    if isinstance(pair, dict):
        pair = pair.get('#text', '')
    if '澳元' in pair and '人民币' in pair:
        print('Entry:')
        print(f'  CurrencyPair: {pair}')
        print(f'  VIPPrice: {item.get("VIPPrice")} (type: {type(item.get("VIPPrice"))})')
        print(f'  Ask: {item.get("Ask")}')
        print(f'  Bid: {item.get("Bid")}')
        print()

