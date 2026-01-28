"""
Check Dadeforex real-time data
"""
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Directly get Dadeforex API
print('Fetching Dadeforex API...')
resp = requests.get('https://www.dadeforex.com/ratelist.json', headers=headers, timeout=10)
data = resp.json()

# Find VIP price AUD/CNY
for item in data.get('data', {}).get('results_rate_json', []):
    pair = item.get('CurrencyPair', '')
    if '澳元' in pair and '人民币' in pair:
        vip = item.get('VIPPrice', 'false')
        ask = item.get('Ask')
        bid = item.get('Bid')
        print('Dadeforex VIP: ask={}, bid={}, vip={}'.format(ask, bid, vip))
        
        # The current scraper mapping
        print('Current scraper: buy=ask={}, sell=bid={}'.format(ask, bid))






