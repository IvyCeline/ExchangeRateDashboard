import requests
from itertools import product

URL = 'https://www.supay.com/wp-admin/admin-ajax.php'
HEADERS = {'User-Agent':'Mozilla/5.0','Referer':'https://www.supay.com/en/'}

actions = ['stm_get_prices','get_prices','get_rate','get_rates','get_exchange_rates']
keys = ['pair','from','to','in','out','currency_from','currency_to','ccy','symbol','currency']
pairs = ['AUD/CNY','AUD-CNY','AUD CNY','AUD','CNY']

tested = []
for action in actions:
    for k in keys:
        for p in pairs:
            payload = {'action': action, k: p}
            try:
                r = requests.post(URL, data=payload, headers=HEADERS, timeout=10)
                ct = r.headers.get('Content-Type','')
                txt = r.text.strip()
                print('ACTION',action,'KEY',k,'PAIR',p,'STATUS',r.status_code,'CT',ct,'LEN',len(txt))
                if txt:
                    print('SNIPPET', txt[:200])
                print('---')
            except Exception as e:
                print('err',action,k,p,e)









