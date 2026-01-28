from playwright.sync_api import sync_playwright
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SITES = {
    'moneychain': 'https://www.moneychain.com.au/exchange-rates/',
    'supay': 'https://www.supay.com/en/',
    'moneychase': 'https://www.moneychase.com.au/currency-rate-page/',
    'gtrading': 'https://www.gtrading.com.au/live-rate',
    'kundaxpay': 'https://www.kundaxpay.com.au/#/realTimeCurrency'
}

NUMBER_RE = re.compile(r'\d+\.\d{3,5}')

def extract_from_text(text):
    nums = NUMBER_RE.findall(text)
    # prefer numbers within reasonable AUD/CNY range
    for n in nums:
        v = float(n)
        if 4.0 < v < 6.0:
            return v
    # fallback first match
    return float(nums[0]) if nums else None

def find_buy_sell_in_page(page):
    # find elements that contain both '澳元' and '人民币' in same text
    elements = page.query_selector_all("body :not(script):not(style)")
    for el in elements:
        try:
            txt = el.inner_text().strip()
        except:
            continue
        if '澳元' in txt and '人民币' in txt:
            # find numbers in this element
            nums = NUMBER_RE.findall(txt)
            if len(nums) >= 2:
                buy = float(nums[0])
                sell = float(nums[1])
                return buy, sell, txt
            elif len(nums) == 1:
                v = float(nums[0])
                return v, v, txt
    # fallback: try table rows with AUD/CNY
    rows = page.query_selector_all('tr')
    for r in rows:
        try:
            txt = r.inner_text().strip()
        except:
            continue
        if 'AUD' in txt or '澳元' in txt:
            nums = NUMBER_RE.findall(txt)
            if len(nums) >= 2:
                return float(nums[0]), float(nums[1]), txt
    return None, None, None

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        for name, url in SITES.items():
            try:
                page = context.new_page()
                page.goto(url, timeout=20000)
                page.wait_for_timeout(2000)
                buy, sell, ctx = find_buy_sell_in_page(page)
                print(f'{name}: buy={buy}, sell={sell}')
                if ctx:
                    print('  context snippet:', ctx[:200].replace('\\n',' '))
                page.close()
            except Exception as e:
                print(f'{name}: error {e}')
        browser.close()

if __name__ == '__main__':
    run()


