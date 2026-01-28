import requests
import json

URL = 'https://www.supay.com/wp-admin/admin-ajax.php'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.supay.com/en/'}

def try_payload(payload):
    try:
        r = requests.post(URL, data=payload, headers=HEADERS, timeout=10)
        print('Payload:', payload)
        print('Status:', r.status_code, 'CT:', r.headers.get('Content-Type'))
        txt = r.text
        print('Len', len(txt))
        snippet = txt.strip()[:1000]
        print('Response snippet:', snippet)
        print('---')
    except Exception as e:
        print('Error', e)

def main():
    # common guesses
    payloads = [
        {'action': 'stm_get_prices'},
        {'action': 'stm_get_prices', 'security': '8f91c6821a'},
        {'action': 'stm_get_prices', 'nonce': '8f91c6821a'},
        {'action': 'get_prices'},
    ]
    for p in payloads:
        try_payload(p)

if __name__ == '__main__':
    main()









