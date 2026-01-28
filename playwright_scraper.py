from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SITES = {
    'supay': 'https://www.supay.com/en/',
    'moneychain': 'https://www.moneychain.com.au/exchange-rates/',
    'moneychase': 'https://www.moneychase.com.au/currency-rate-page/',
    'gtrading': 'https://www.gtrading.com.au/live-rate',
    'kundaxpay': 'https://www.kundaxpay.com.au/#/realTimeCurrency'
}

def extract_table_like_rows(page):
    """通用策略：查找页面中所有行（tr或类似的列表项），返回包含文本和单元格列表的记录"""
    rows = []
    # 尝试表格行
    trs = page.query_selector_all('tr')
    for tr in trs:
        texts = [td.inner_text().strip() for td in tr.query_selector_all('th,td')]
        if texts:
            rows.append(texts)
    # 如果没有表格行，尝试列表项或自定义行容器
    if not rows:
        items = page.query_selector_all('li, .rate-row, .currency-row, .rate-item, .live-rate-row')
        for it in items:
            txt = it.inner_text().strip()
            # split by newline
            cells = [c.strip() for c in txt.split('\\n') if c.strip()]
            if cells:
                rows.append(cells)
    return rows

def find_aud_cny(rows):
    """从 rows 中寻找包含澳元和人民币的行，返回买/卖值（尽量按现汇买入/现汇卖出）"""
    import re
    for r in rows:
        joined = ' '.join(r)
        if ('澳元' in joined or 'AUD' in joined) and ('人民币' in joined or 'CNY' in joined):
            # find all numbers in row
            nums = re.findall(r'\\d+\\.\\d{1,5}', joined)
            # Heuristic orders vary; common patterns: [label, buy, sell] or [pair, buy, sell]
            if len(nums) >= 2:
                # choose first two as buy/sell
                buy = float(nums[0])
                sell = float(nums[1])
                return {'buy': buy, 'sell': sell, 'raw_row': r}
    return None

def scrape_site(name, url):
    logger.info(f'Scraping (rendered) {name}: {url}')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        # allow some time for dynamic content
        page.wait_for_timeout(2500)
        # Use a JS-based search for elements that mention 澳元 and 人民币 (or AUD/CNY)
        try:
            found = page.evaluate("""() => {
                const elems = Array.from(document.querySelectorAll('body *'));
                const out = [];
                for (let el of elems) {
                    const t = (el.innerText || '').trim();
                    if (!t) continue;
                    if (/(澳元[\\s\\S]*?人民币|AUD[\\s\\S]*?CNY)/i.test(t)) {
                        const nums = Array.from((t.match(/\\d+\\.\\d{1,5}/g) || []));
                        // collect numbers from next 3 siblings
                        const neighbor_nums = [];
                        let ns = el.nextElementSibling;
                        for (let i=0;i<3 && ns;i++) {
                            neighbor_nums.push(...(Array.from((ns.innerText||'').match(/\\d+\\.\\d{1,5}/g) || [])));
                            ns = ns.nextElementSibling;
                        }
                        out.push({text: t.slice(0,400), nums: nums, neighbor_nums: neighbor_nums});
                        if (out.length >= 8) break;
                    }
                }
                return out;
            }""")
        except Exception:
            found = []

        result = None
        if found:
            # choose the first entry that yields at least two numeric values (buy and sell)
            import re
            for entry in found:
                nums = entry.get('nums',[]) + entry.get('neighbor_nums',[])
                # flatten and remove duplicates preserving order
                seen = set(); flat=[]
                for n in nums:
                    if n not in seen:
                        seen.add(n); flat.append(n)
                if len(flat) >= 2:
                    try:
                        buy = float(flat[0]); sell = float(flat[1])
                        result = {'buy': buy, 'sell': sell, 'context': entry['text']}
                        break
                    except:
                        continue
        # fallback: previous table-like extraction
        if not result:
            rows = extract_table_like_rows(page)
            result = find_aud_cny(rows)
        browser.close()
        return result

def main():
    out = {}
    for name, url in SITES.items():
        try:
            r = scrape_site(name, url)
            out[name] = r or {}
        except Exception as e:
            logger.error(f'Error scraping {name}: {e}')
            out[name] = {'error': str(e)}
    out['timestamp'] = datetime.now().isoformat()
    # write output to file to avoid console encoding issues
    with open('playwright_out.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()


