import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import logging
from playwright.sync_api import sync_playwright

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExchangeRateScraper:
    def __init__(self):
        self.companies = {
            'moneychain': 'https://www.moneychain.com.au/exchange-rates/',
            'supay': 'https://www.supay.com/en/',
            'moneychase': 'https://www.moneychase.com.au/currency-rate-page/',
            'dadeforex': 'https://www.dadeforex.com/',
            'gtrading': 'https://www.gtrading.com.au/live-rate',
            'kundaxpay': 'https://www.kundaxpay.com.au/#/realTimeCurrency'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_moneychain(self):
        """抓取Moneychain的汇率"""
        try:
            url = self.companies['moneychain']
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            rates = {}

            # 优先查找页面中是否同时给出买入/卖出字段（带关键词“买入”“卖出”或“buy”“sell”）
            page_text = soup.get_text(separator='\n')
            import re
            buy_match = re.search(r'(现汇买入价|现汇买入|买入价|buy price|buy)\s*[:：]?\s*(\\d+\\.\\d+)', page_text, re.I)
            sell_match = re.search(r'(现汇卖出价|现汇卖出|卖出价|sell price|sell)\s*[:：]?\s*(\\d+\\.\\d+)', page_text, re.I)
            logger.info(f"Moneychain: buy_match={bool(buy_match)}, sell_match={bool(sell_match)}")

            if buy_match and sell_match:
                try:
                    buy = float(buy_match.group(2))
                    sell = float(sell_match.group(2))
                    rates['AUD_CNY'] = {'buy': buy, 'sell': sell}
                    return rates
                except:
                    pass

            # Try scanning individual elements to find the specific '澳元 -> 人民币' line
            try:
                for el in soup.find_all(True):
                    txt = el.get_text(separator='\n').strip()
                    if '澳元' in txt and '人民币' in txt and ('→' in txt or '->' in txt or '/' in txt):
                        lines = [l.strip() for l in txt.splitlines() if l.strip()]
                        for ln_idx, ln in enumerate(lines):
                            if '澳元' in ln and '人民币' in ln:
                                nums = re.findall(r'\\d+\\.\\d{1,5}', ln)
                                if len(nums) >= 2:
                                    return {'AUD_CNY': {'buy': float(nums[0]), 'sell': float(nums[1])}}
                                # look in following lines for numbers (line with VIP then numbers)
                                for follow in lines[ln_idx+1:ln_idx+6]:
                                    more = re.findall(r'\\d+\\.\\d{1,5}', follow)
                                    if len(more) >= 2:
                                        return {'AUD_CNY': {'buy': float(more[0]), 'sell': float(more[1])}}
                                    if len(more) == 1 and len(nums) == 1:
                                        return {'AUD_CNY': {'buy': float(nums[0]), 'sell': float(more[0])}}
            except Exception:
                pass

            mid_rate = None
            # 作为兜底，扫描页面中出现的明显汇率数字
            if not mid_rate:
                all_numbers = re.findall(r'\\d+\\.\\d{3,5}', page_text)
                for n in all_numbers:
                    try:
                        val = float(n)
                        if 4.0 < val < 6.0:
                            mid_rate = val
                            break
                    except:
                        continue

            if mid_rate:
                # 如果网站没有提供买卖价，按默认spread估算（可调整为更合适的百分比）
                spread_pct = 0.0015  # 0.15% 默认点差
                buy = round(mid_rate * (1 - spread_pct), 4)
                sell = round(mid_rate * (1 + spread_pct), 4)
                rates['AUD_CNY'] = {'buy': buy, 'sell': sell, 'source_mid': mid_rate, 'spread_pct': spread_pct}
                return rates
            # fallback: try Playwright to extract AUD/CNY row
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    page.wait_for_timeout(1500)
                    found = page.evaluate('''() => {
                        const selectors = ['.header_currency', '.header_currency_swiper', '.content', '.rate-item', '.rate-list', '.rate-table', '.rates-table'];
                        function extractFromText(t) {
                            const lines = t.split(/\\r?\\n/).map(s=>s.trim()).filter(Boolean);
                            // prefer lines that explicitly contain VIP
                            for (let i=0;i<lines.length;i++) {
                                const ln = lines[i];
                                if (/vip/i.test(ln) && /澳元/.test(ln) && /人民币/.test(ln)) {
                                    const nums = (ln.match(/\\d+\\.\\d{1,5}/g) || []);
                                    if (nums.length>=2) return [nums[0], nums[1]];
                                }
                            }
                            // otherwise find line with pair, then numbers on same or following lines
                            for (let i=0;i<lines.length;i++) {
                                const ln = lines[i];
                                if (/澳元/.test(ln) && /人民币/.test(ln) || /AUD/.test(ln) && /CNY/.test(ln)) {
                                    let nums = (ln.match(/\\d+\\.\\d{1,5}/g) || []);
                                    if (nums.length>=2) return [nums[0], nums[1]];
                                    for (let j=i+1;j<Math.min(i+4, lines.length); j++) {
                                        const more = (lines[j].match(/\\d+\\.\\d{1,5}/g) || []);
                                        if (more.length>=2) return [more[0], more[1]];
                                        if (more.length==1 && nums.length==1) return [nums[0], more[0]];
                                    }
                                }
                            }
                            return null;
                        }
                        for (let sel of selectors) {
                            const el = document.querySelector(sel);
                            if (!el) continue;
                            const t = (el.innerText||'').trim();
                            const res = extractFromText(t);
                            if (res) return res;
                        }
                        // final fallback: scan body
                        const bodyText = (document.body.innerText||'').trim();
                        return extractFromText(bodyText);
                    }''')
                    browser.close()
                    if found:
                        try:
                            return {'AUD_CNY': {'buy': float(found[0]), 'sell': float(found[1])}}
                        except:
                            pass
            except Exception:
                pass
            return None

        except Exception as e:
            logger.error(f"Error scraping Moneychain: {e}")
            return None

    def scrape_supay(self):
        """抓取Supay的汇率 - 从 rate.php iframe URL 直接提取 VIP 行数据"""
        try:
            # Supay 的汇率数据在 iframe 中加载，直接访问该 URL
            iframe_url = 'https://www.supay.com/rate.php?lang=en'
            
            def extract_from_iframe(url):
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.set_default_timeout(30000)
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    page.wait_for_timeout(2000)
                    
                    # 查找表格中的 VIP 行
                    result = page.evaluate("""
                        () => {
                            const rows = document.querySelectorAll('tr');

                            // 优先查找 VIP 行
                            for (let row of rows) {
                                const text = row.innerText || '';
                                if (text.toLowerCase().includes('vip') &&
                                    (text.includes('AUD') || text.includes('CNY'))) {

                                    const cells = Array.from(row.querySelectorAll('td, th')).map(td => td.innerText.trim());

                                    // 查找所有 4.xxxx 格式的价格
                                    const allPrices = cells.filter(t => /^4\\.\\d{4}$/.test(t));

                                    // 同时查找标签 (BidTT, AskTT)
                                    const bidIndex = cells.findIndex(c => c.includes('BidTT'));
                                    const askIndex = cells.findIndex(c => c.includes('AskTT'));

                                    if (allPrices.length >= 2) {
                                        // 如果能找到 BidTT 和 AskTT 标签，按标签位置取价格
                                        if (bidIndex >= 0 && askIndex >= 0) {
                                            // 获取标签旁边的价格
                                            const bidPrice = cells[bidIndex + 1];
                                            const askPrice = cells[askIndex + 1];
                                            if (/^4\\.\\d{4}$/.test(bidPrice) && /^4\\.\\d{4}$/.test(askPrice)) {
                                                return {
                                                    found: true,
                                                    type: 'vip_labeled',
                                                    buy: bidPrice,    // BidTT = 我们买入的价格
                                                    sell: askPrice,   // AskTT = 我们卖出的价格
                                                    full_row: text
                                                };
                                            }
                                        }

                                        // 如果没有标签，按价格大小判断（Bid > Ask）
                                        const sortedPrices = [...allPrices].sort((a, b) => parseFloat(b) - parseFloat(a));
                                        const higherPrice = sortedPrices[0];
                                        const lowerPrice = sortedPrices[allPrices.length - 1];

                                        return {
                                            found: true,
                                            type: 'vip_sorted',
                                            buy: higherPrice,  // 较高的价格 = 买入价
                                            sell: lowerPrice,  // 较低的价格 = 卖出价
                                            all_prices: allPrices,
                                            full_row: text
                                        };
                                    }
                                }
                            }

                            // 如果没有 VIP 行，查找 AUD/CNY 行
                            for (let row of rows) {
                                const text = row.innerText || '';
                                if ((text.includes('AUD/CNY') || text.includes('AUD CNY')) &&
                                    !text.toLowerCase().includes('pair')) {

                                    const cells = Array.from(row.querySelectorAll('td, th')).map(td => td.innerText.trim());
                                    const all_prices = cells.filter(t => /^4\\.\\d{4}$/.test(t));

                                    // 查找标签
                                    const bidIndex = cells.findIndex(c => c.includes('BidTT'));
                                    const askIndex = cells.findIndex(c => c.includes('AskTT'));

                                    if (all_prices.length >= 2) {
                                        if (bidIndex >= 0 && askIndex >= 0) {
                                            const bidPrice = cells[bidIndex + 1];
                                            const askPrice = cells[askIndex + 1];
                                            if (/^4\\.\\d{4}$/.test(bidPrice) && /^4\\.\\d{4}$/.test(askPrice)) {
                                                return {
                                                    found: true,
                                                    type: 'regular_labeled',
                                                    buy: bidPrice,
                                                    sell: askPrice,
                                                    full_row: text
                                                };
                                            }
                                        }

                                        // 按价格大小排序
                                        const sortedPrices = [...all_prices].sort((a, b) => parseFloat(b) - parseFloat(a));
                                        return {
                                            found: true,
                                            type: 'regular_sorted',
                                            buy: sortedPrices[0],
                                            sell: sortedPrices[sortedPrices.length - 1],
                                            all_prices: all_prices,
                                            full_row: text
                                        };
                                    }
                                }
                            }

                            return {found: false};
                        }
                    """)
                    
                    browser.close()
                    return result
            
            # 直接从 iframe URL 提取数据
            result = extract_from_iframe(iframe_url)

            if result and result.get('found'):
                try:
                    # 确保 buy > sell（买入价应该高于卖出价）
                    buy_price = float(result['buy'])
                    sell_price = float(result['sell'])

                    # 如果 buy <= sell，说明顺序反了，需要交换
                    if buy_price <= sell_price:
                        logger.warning("Supay: buy ({}) <= sell ({}), swapping values".format(buy_price, sell_price))
                        buy_price, sell_price = sell_price, buy_price

                    logger.info("Supay: type={}, buy={}, sell={}".format(
                        result.get('type', 'unknown'), buy_price, sell_price
                    ))
                    return {'AUD_CNY': {'buy': buy_price, 'sell': sell_price}}
                except (ValueError, KeyError) as e:
                    logger.error("Supay: Failed to parse prices: {}, result={}".format(e, result))
            
            # 如果 Playwright 失败，尝试简单的 requests
            try:
                response = requests.get(iframe_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 5:
                            cell_texts = [c.get_text().strip() for c in cells]
                            
                            if 'VIP' in cell_texts[0] and 'AUD' in str(cell_texts):
                                prices = [t for t in cell_texts if re.match(r'^4\\.\\d{4}$', t)]
                                if len(prices) >= 2:
                                    # 按价格大小排序后赋值，确保 buy > sell
                                    float_prices = [float(p) for p in prices]
                                    buy_price = max(float_prices)
                                    sell_price = min(float_prices)
                                    return {'AUD_CNY': {'buy': buy_price, 'sell': sell_price}}
            except Exception as e:
                logger.error(f"Supay fallback requests failed: {e}")
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}

        except Exception as e:
            logger.error(f"Error scraping Supay: {e}")
            return None

    def scrape_moneychase(self):
        """抓取Moneychase的汇率"""
        try:
            url = self.companies['moneychase']
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            rates = {}

            # 从页面中查找汇率表格
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        currency_pair = cells[0].get_text().strip()
                        buy_price = cells[1].get_text().strip()
                        sell_price = cells[2].get_text().strip()

                        if '澳元/人民币' in currency_pair or 'AUD/CNY' in currency_pair:
                            try:
                                buy = float(buy_price) if buy_price else None
                                sell = float(sell_price) if sell_price else None
                                rates['AUD_CNY'] = {'buy': buy, 'sell': sell}
                                break
                            except:
                                continue

            # 如果表格中没有数据，尝试查找JavaScript中的数据
            if not rates:
                scripts = soup.find_all('script')
                for script in scripts:
                    script_text = script.get_text() if script.get_text() else ''
                    if 'rate' in script_text.lower() or '汇率' in script_text:
                        # 查找数字模式
                        import re
                        rate_pattern = re.compile(r'(\d+\.\d+)')
                        matches = rate_pattern.findall(script_text)
                        if matches:
                            # 假设第一个匹配的是AUD到CNY的汇率
                            try:
                                rate = float(matches[0])
                                if 4.0 < rate < 6.0:
                                    rates['AUD_CNY'] = {'buy': rate, 'sell': rate}
                            except:
                                pass
            # fallback: render with Playwright to extract AUD/CNY row
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    page.wait_for_timeout(1500)
                    found = page.evaluate('''() => {
                        const rows = Array.from(document.querySelectorAll('tr, li, div'));
                        for (let el of rows) {
                            const t = (el.innerText||'').trim();
                            if (/(澳元|AUD)/i.test(t) && /(人民币|CNY)/i.test(t)) {
                                const nums = (t.match(/\\d+\\.\\d{1,5}/g) || []);
                                if (nums.length>=2) return [nums[0], nums[1]];
                            }
                        }
                        return null;
                    }''')
                    browser.close()
                    if found:
                        try:
                            return {'AUD_CNY': {'buy': float(found[0]), 'sell': float(found[1])}}
                        except:
                            pass
            except Exception:
                pass

            return rates if rates else None

        except Exception as e:
            logger.error(f"Error scraping Moneychase: {e}")
            return None

    def scrape_dadeforex(self):
        """抓取Dadeforex的汇率 - 从网页直接抓取实时数据"""
        try:
            url = self.companies['dadeforex']

            # 直接使用 Playwright 从网页抓取
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_viewport_size({"width": 1920, "height": 1080})

                # 添加随机参数避免缓存
                import time
                cache_buster = int(time.time() * 1000)
                page.goto(f"{url}?_={cache_buster}", wait_until="domcontentloaded", timeout=30000)

                # 等待页面加载
                page.wait_for_timeout(3000)

                # 从页面提取数据 - 优先 VIP 行
                result = page.evaluate("""
                    () => {
                        // 查找所有包含澳元/人民币的行
                        const rows = document.querySelectorAll('div.divRow, tr');

                        let vip_row = null;
                        let regular_row = null;

                        for (let row of rows) {
                            const text = row.innerText || '';
                            const cells = Array.from(row.querySelectorAll('div, td')).map(td => td.innerText.trim());

                            // 查找澳元/人民币行
                            if ((text.includes('澳元') || text.includes('AUD')) &&
                                (text.includes('人民币') || text.includes('CNY'))) {

                                // 查找 4.xxxx 格式的价格
                                const prices = cells.filter(c => /^4\\.\\d{4}$/.test(c));

                                if (prices.length >= 2) {
                                    // 区分 VIP 和普通行
                                    if (text.toLowerCase().includes('vip') || cells.some(c => c.includes('VIP'))) {
                                        if (!vip_row) {
                                            vip_row = {
                                                cells: cells,
                                                prices: prices,
                                                text: text
                                            };
                                        }
                                    } else if (!regular_row) {
                                        regular_row = {
                                            cells: cells,
                                            prices: prices,
                                            text: text
                                        };
                                    }
                                }
                            }
                        }

                        // 优先使用 VIP 行
                        const selected = vip_row || regular_row;

                        if (selected) {
                            console.log('Dadeforex found:', selected.cells);

                            // 页面显示格式：第一个价格是买入价，第二个是卖出价
                            // 即 buy > sell（买入价高于卖出价）
                            const prices = selected.prices;
                            const float_prices = prices.map(p => parseFloat(p));

                            // 如果第一个价格 > 第二个，则 buy=prices[0], sell=prices[1]
                            // 否则交换
                            let buy, sell;
                            if (float_prices[0] > float_prices[1]) {
                                buy = float_prices[0];
                                sell = float_prices[1];
                            } else {
                                buy = float_prices[1];
                                sell = float_prices[0];
                            }

                            return {
                                found: true,
                                buy: buy.toFixed(4),
                                sell: sell.toFixed(4),
                                is_vip: vip_row !== null,
                                method: vip_row ? 'vip_row' : 'regular_row'
                            };
                        }

                        return {found: false};
                    }
                """)

                browser.close()

                if result and result.get('found'):
                    try:
                        buy = float(result['buy'])
                        sell = float(result['sell'])

                        logger.info("Dadeforex: buy={}, sell={}, is_vip={}, method={}".format(
                            buy, sell, result.get('is_vip'), result.get('method', 'unknown')
                        ))
                        return {'AUD_CNY': {'buy': buy, 'sell': sell}}

                    except Exception as e:
                        logger.error("Dadeforex: Failed to parse prices: {}, result={}".format(e, result))

            logger.warning("Dadeforex: Could not find AUD/CNY data from web")
            return {'AUD_CNY': {'buy': None, 'sell': None}}

        except Exception as e:
            logger.error("Error scraping Dadeforex: {}".format(e))
            return None

            # 兜底：尝试从页面中解析
            url = self.companies['dadeforex']
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            import re
            nums = re.findall(r'\d+\.\d{3,5}', page_text)
            for n in nums:
                v = float(n)
                if 4.0 < v < 6.0:
                    return {'AUD_CNY': {'buy': v, 'sell': v}}
            return None

        except Exception as e:
            logger.error("Error scraping Dadeforex: {}".format(e))
            return None

    def scrape_gtrading(self):
        """抓取GTrading的汇率"""
        try:
            url = self.companies['gtrading']
            # try simple requests parse first
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                # search for tables and prefer 现汇 (TT) columns if present
                tables = soup.find_all('table')
                for table in tables:
                    # find header texts
                    headers = [th.get_text().strip() for th in table.find_all('th')]
                    buy_idx = sell_idx = None
                    for i, h in enumerate(headers):
                        if '现汇买' in h or '现汇买入' in h or '现汇买入价' in h or 'WE SELL TT' in h.upper():
                            buy_idx = i
                        if '现汇卖' in h or '现汇卖出' in h or '现汇卖出价' in h or 'WE BUY TT' in h.upper():
                            sell_idx = i
                    # if both indices found, find row with AUD/CNY
                    if buy_idx is not None and sell_idx is not None:
                        for row in table.find_all('tr'):
                            cells = row.find_all(['td','th'])
                            joined = ' '.join([c.get_text().strip() for c in cells])
                            if '澳元' in joined and '人民币' in joined or 'AUD' in joined and 'CNY' in joined:
                                try:
                                    buy_text = cells[buy_idx].get_text().strip()
                                    sell_text = cells[sell_idx].get_text().strip()
                                    buy = float(buy_text)
                                    sell = float(sell_text)
                                    return {'AUD_CNY': {'buy': buy, 'sell': sell}}
                                except Exception:
                                    continue
                # fallback: look for any row containing 澳元 and 人民币 and pick numbers (less preferred)
                for row in soup.find_all(['tr','div','li']):
                    txt = row.get_text(separator=' ', strip=True)
                    if '澳元' in txt and '人民币' in txt:
                        import re
                        nums = re.findall(r'\\d+\\.\\d{1,5}', txt)
                        if len(nums) >= 2:
                            return {'AUD_CNY': {'buy': float(nums[0]), 'sell': float(nums[1])}}
            except Exception:
                pass

            # fallback: render with Playwright and prefer TT columns
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(1500)
                found = page.evaluate('''() => {
                    // find table, header indices, then the AUD/CNY row
                    const tables = Array.from(document.querySelectorAll('table'));
                    for (let table of tables) {
                        const ths = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
                        let buy_idx = -1, sell_idx = -1;
                        for (let i=0;i<ths.length;i++) {
                            const h = ths[i];
                            if (/现汇买/i.test(h) || /WE SELL TT/i.test(h)) buy_idx = i;
                            if (/现汇卖/i.test(h) || /WE BUY TT/i.test(h)) sell_idx = i;
                        }
                        if (buy_idx >=0 && sell_idx >=0) {
                            const rows = Array.from(table.querySelectorAll('tr'));
                            for (let r of rows) {
                                const txt = (r.innerText||'').trim();
                                if (/澳元/.test(txt) && /人民币/.test(txt) || /AUD/.test(txt) && /CNY/.test(txt)) {
                                    const cells = Array.from(r.querySelectorAll('td,th')).map(c=>c.innerText.trim());
                                    if (cells[buy_idx] && cells[sell_idx]) return {buy: cells[buy_idx], sell: cells[sell_idx]};
                                }
                            }
                        }
                    }
                    // fallback generic find
                    const rows = Array.from(document.querySelectorAll('tr, li, div'));
                    for (let el of rows) {
                        const t = (el.innerText||'').trim();
                        if (/澳元/.test(t) && /人民币/.test(t) || /AUD/.test(t) && /CNY/.test(t)) {
                            const nums = (t.match(/\\d+\\.\\d{1,5}/g) || []);
                            if (nums.length>=2) return {buy: nums[0], sell: nums[1]};
                        }
                    }
                    return null;
                }''')
                browser.close()
                if found and isinstance(found, dict):
                    try:
                        b = float(found.get('buy')) if found.get('buy') else None
                        s = float(found.get('sell')) if found.get('sell') else None
                        return {'AUD_CNY': {'buy': b, 'sell': s}}
                    except:
                        pass
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error(f"Error scraping GTrading: {e}")
            return None

    def scrape_kundaxpay(self):
        """抓取Kundaxpay的汇率 - 精确提取现汇买入/卖出价"""
        try:
            url = self.companies['kundaxpay']

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_viewport_size({"width": 1920, "height": 1080})
                page.goto(url, wait_until="domcontentloaded", timeout=60000)

                # 等待 Angular 应用加载完成
                try:
                    # 等待页面有表格或汇率数据加载
                    page.wait_for_function(
                        "document.querySelector('table') !== null || document.querySelector('.currency') !== null || document.querySelector('[class*=\"rate\"]') !== null",
                        timeout=15000
                    )
                except Exception:
                    pass

                # 额外等待数据渲染
                page.wait_for_timeout(8000)

                # 尝试多种方式查找 AUD/CNY 行
                result = page.evaluate('''
                    () => {
                        // 方式1: 直接查找表格行
                        const rows = document.querySelectorAll('tr');
                        for (let row of rows) {
                            const cells = Array.from(row.querySelectorAll('td')).map(td => td.innerText.trim());
                            const rowText = row.innerText || '';

                            if ((rowText.includes('AUD') || rowText.includes('CNY') || rowText.includes('澳元') || rowText.includes('人民币')) &&
                                (rowText.includes('AUD') || rowText.includes('CNY')) &&
                                cells.length >= 5) {

                                // 打印所有单元格用于调试
                                console.log('找到行:', cells);

                                // 查找 4.xxxx 格式的汇率
                                const pricePattern = /^4\\.\\d{4}$/;
                                const prices = cells.filter(c => pricePattern.test(c));

                                if (prices.length >= 2) {
                                    // 通常 cells[3] 是买入价, cells[4] 是卖出价
                                    // 但需要验证顺序
                                    return {
                                        found: true,
                                        buy: cells[3],
                                        sell: cells[4],
                                        prices: prices,
                                        allCells: cells,
                                        method: 'table_row'
                                    };
                                }
                            }
                        }

                        // 方式2: 查找包含汇率数据的 div/span
                        const allElements = document.querySelectorAll('div, span, td');
                        let dataRows = [];
                        for (let el of allElements) {
                            const text = el.innerText || '';
                            if ((text.includes('AUD') || text.includes('CNY')) &&
                                /4\\.\\d{3,5}/.test(text)) {
                                dataRows.push({
                                    text: text,
                                    tag: el.tagName
                                });
                            }
                        }

                        // 方式3: 查找表格数据
                        const tables = document.querySelectorAll('table');
                        for (let table of tables) {
                            const tableText = table.innerText || '';
                            if (tableText.includes('AUD') && tableText.includes('CNY')) {
                                const rows = table.querySelectorAll('tr');
                                for (let row of rows) {
                                    const cells = Array.from(row.querySelectorAll('td, th')).map(td => td.innerText.trim());
                                    const rowText = row.innerText || '';

                                    if (cells.length >= 5 && /4\\.\\d{4}/.test(cells[3]) && /4\\.\\d{4}/.test(cells[4])) {
                                        return {
                                            found: true,
                                            buy: cells[3],
                                            sell: cells[4],
                                            allCells: cells,
                                            method: 'table_cell'
                                        };
                                    }
                                }
                            }
                        }

                        return {found: false, dataRows: dataRows.slice(0, 5)};
                    }
                ''')

                browser.close()

                if result and result.get('found'):
                    try:
                        buy = float(result['buy'])
                        sell = float(result['sell'])

                        # 确保 buy > sell（买入价应该高于卖出价）
                        if buy <= sell:
                            logger.warning("Kundaxpay: buy ({}) <= sell ({}), swapping values".format(buy, sell))
                            buy, sell = sell, buy

                        logger.info("Kundaxpay: buy={}, sell={}, method={}".format(buy, sell, result.get('method', 'unknown')))
                        return {'AUD_CNY': {'buy': buy, 'sell': sell}}
                    except (ValueError, TypeError) as e:
                        logger.error("Kundaxpay: Failed to parse numbers: {}, result={}".format(e, result))

                logger.warning("Kundaxpay: Could not find AUD/CNY data")
                return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error("Error scraping Kundaxpay: {}".format(e))
            return None

    def scrape_all_companies(self):
        """并行抓取所有公司的汇率"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        all_rates = {}
        
        scrapers = {
            'moneychain': self.scrape_moneychain,
            'supay': self.scrape_supay,
            'moneychase': self.scrape_moneychase,
            'dadeforex': self.scrape_dadeforex,
            'gtrading': self.scrape_gtrading,
            'kundaxpay': self.scrape_kundaxpay
        }
        
        # 并行抓取所有网站
        def scrape_company(name_scraper):
            name, scraper = name_scraper
            try:
                rates = scraper()
                return name, rates
            except Exception as e:
                logger.error(f"Error scraping {name}: {e}")
                return name, None
        
        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(scrape_company, item): item[0] for item in scrapers.items()}
            
            for future in as_completed(futures):
                name, rates = future.result()
                if rates:
                    all_rates[name] = rates
        
        # 添加时间戳
        all_rates['timestamp'] = datetime.now().isoformat()
        
        return all_rates

    def save_rates(self, rates, filename='exchange_rates.json'):
        """保存汇率数据到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(rates, f, indent=2, ensure_ascii=False)
            logger.info(f"Rates saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving rates: {e}")

    def load_rates(self, filename='exchange_rates.json'):
        """从文件加载汇率数据"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"Error loading rates: {e}")
            return {}

if __name__ == "__main__":
    scraper = ExchangeRateScraper()
    rates = scraper.scrape_all_companies()
    print(json.dumps(rates, indent=2, ensure_ascii=False))
    scraper.save_rates(rates)
