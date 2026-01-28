"""
Test websites data
"""
import requests
from bs4 import BeautifulSoup
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def test_dadeforex():
    print('=== Dadeforex Website Data ===')
    try:
        # Try JSON API first
        try:
            json_r = requests.get('https://www.dadeforex.com/ratelist.json', headers=headers, timeout=10)
            data = json_r.json()
            print('JSON API Response:')
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1500])
        except Exception as e:
            print(f'JSON API Error: {e}')
    except Exception as e:
        print(f'Error: {e}')

def test_gtrading():
    print('\n=== GTrading Website Data ===')
    try:
        r = requests.get('https://www.gtrading.com.au/live-rate', headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        # Find tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_texts = [c.get_text().strip() for c in cells]
                if any('AUD' in t and 'CNY' in t for t in cell_texts):
                    print('Row: ' + ' | '.join(cell_texts))
    except Exception as e:
        print(f'Error: {e}')

def test_kundaxpay():
    print('\n=== Kundaxpay Website Data ===')
    try:
        # Kundaxpay is SPA, need Playwright
        print('Kundaxpay is SPA dynamic page, needs Playwright')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_dadeforex()
    test_gtrading()
    test_kundaxpay()
