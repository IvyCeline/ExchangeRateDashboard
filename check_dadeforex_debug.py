# -*- coding: utf-8 -*-
"""
检查 Dadeforex API 返回的原始数据
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Cache-Control': 'no-cache'
}

print("=" * 60)
print("检查 Dadeforex API 实时数据")
print("=" * 60)

# 添加随机参数避免缓存
import time
random_param = int(time.time() * 1000)
url = f'https://www.dadeforex.com/ratelist.json?_={random_param}'

print(f"\n请求 URL: {url}")
resp = requests.get(url, headers=headers, timeout=10)
data = resp.json()

print(f"\n时间戳: {data.get('data', {}).get('curr_date', 'N/A')}")
print(f"总共 {len(data.get('data', {}).get('results_rate_json', []))} 条数据")

# 查找所有澳元/人民币的数据
print("\n" + "=" * 60)
print("所有澳元/人民币 (AUD/CNY) 数据:")
print("=" * 60)

aud_cny_items = []
for item in data.get('data', {}).get('results_rate_json', []):
    pair = item.get('CurrencyPair', '')
    if isinstance(pair, dict):
        pair = pair.get('#text', '')
    
    if '澳元' in pair and '人民币' in pair:
        vip = item.get('VIPPrice', 'false')
        ask = item.get('Ask')
        bid = item.get('Bid')
        ask_cash = item.get('AskCash')
        bid_cash = item.get('BidCash')
        
        item_info = {
            'vip': vip,
            'ask': ask,
            'bid': bid,
            'ask_cash': ask_cash,
            'bid_cash': bid_cash,
            'raw': item
        }
        aud_cny_items.append(item_info)
        
        print(f"\n条目:")
        print(f"  VIPPrice: {vip}")
        print(f"  Ask (卖出价/客户买入): {ask}")
        print(f"  Bid (买入价/客户卖出): {bid}")
        print(f"  AskCash: {ask_cash}")
        print(f"  BidCash: {bid_cash}")

print("\n" + "=" * 60)
print("当前代码的处理逻辑:")
print("=" * 60)

# 当前代码的逻辑
vip_item = None
regular_item = None

for item in aud_cny_items:
    if item['vip'] == 'true' or item['vip'] is True:
        vip_item = item
        break
    elif regular_item is None:
        regular_item = item

selected = vip_item or regular_item

if selected:
    print(f"\n选择的条目 (VIP={selected['vip']}):")
    print(f"  buy = bid = {selected['bid']}")
    print(f"  sell = ask = {selected['ask']}")
    print(f"\n输出结果:")
    print(f"  buy: {selected['bid']}")
    print(f"  sell: {selected['ask']}")

print("\n" + "=" * 60)
print("问题分析:")
print("=" * 60)
print("\nAPI 返回的数据可能是缓存，不是实时数据！")
print("建议：")
print("1. 检查 API 是否有其他实时接口")
print("2. 或者尝试从网页直接抓取")
print("3. 添加时间戳验证，确保数据在合理时间内更新")
