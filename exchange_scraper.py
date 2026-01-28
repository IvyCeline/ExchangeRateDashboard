import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import logging
import gc

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

    def scrape_moneychain(self):
        """抓取Moneychain的汇率"""
        try:
            url = self.companies['moneychain']
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            page_text = soup.get_text(separator='\n')
            import re
            
            # 查找买入/卖出价
            buy_match = re.search(r'(现汇买入价|现汇买入|买入价|buy price|buy)\s*[:：]?\s*(\d+\.\d+)', page_text, re.I)
            sell_match = re.search(r'(现汇卖出价|现汇卖出|卖出价|sell price|sell)\s*[:：]?\s*(\d+\.\d+)', page_text, re.I)
            
            if buy_match and sell_match:
                buy = float(buy_match.group(2))
                sell = float(sell_match.group(2))
                logger.info("Moneychain: buy={}, sell={}".format(buy, sell))
                return {'AUD_CNY': {'buy': buy, 'sell': sell}}
            
            # 查找表格数据
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        cell_texts = [c.get_text().strip() for c in cells]
                        if '澳元' in str(cell_texts) and '人民币' in str(cell_texts):
                            try:
                                nums = [float(re.search(r'\d+\.\d+', c).group()) for c in cell_texts if re.search(r'\d+\.\d+', c)]
                                if len(nums) >= 2:
                                    return {'AUD_CNY': {'buy': nums[0], 'sell': nums[1]}}
                            except:
                                continue
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error("Moneychain error: {}".format(e))
            return {'AUD_CNY': {'buy': None, 'sell': None}}

    def scrape_supay(self):
        """抓取Supay的汇率"""
        try:
            url = 'https://www.supay.com/rate.php?lang=en'
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            import re
            
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 5:
                        cell_texts = [c.get_text().strip() for c in cells]
                        
                        if 'VIP' in cell_texts[0] and 'AUD' in str(cell_texts):
                            prices = [t for t in cell_texts if re.match(r'^4\.\d{4}$', t)]
                            if len(prices) >= 2:
                                float_prices = [float(p) for p in prices]
                                buy = max(float_prices)
                                sell = min(float_prices)
                                logger.info("Supay: buy={}, sell={}".format(buy, sell))
                                return {'AUD_CNY': {'buy': buy, 'sell': sell}}
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error("Supay error: {}".format(e))
            return {'AUD_CNY': {'buy': None, 'sell': None}}

    def scrape_moneychase(self):
        """抓取Moneychase的汇率"""
        try:
            url = self.companies['moneychase']
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            import re
            
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        currency_pair = cells[0].get_text().strip()
                        if '澳元' in currency_pair and '人民币' in currency_pair:
                            try:
                                buy = float(cells[1].get_text().strip())
                                sell = float(cells[2].get_text().strip())
                                if buy and sell:
                                    logger.info("Moneychase: buy={}, sell={}".format(buy, sell))
                                    return {'AUD_CNY': {'buy': buy, 'sell': sell}}
                            except:
                                continue
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error("Moneychase error: {}".format(e))
            return {'AUD_CNY': {'buy': None, 'sell': None}}

    def scrape_dadeforex(self):
        """抓取Dadeforex的汇率"""
        try:
            # 直接从网页抓取
            url = self.companies['dadeforex']
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            import re
            
            # 查找澳元/人民币行
            rows = soup.find_all('div', class_='divRow')
            for row in rows:
                text = row.get_text()
                if ('澳元' in text or 'AUD' in text) and ('人民币' in text or 'CNY' in text):
                    prices = re.findall(r'4\.\d{4}', text)
                    if len(prices) >= 2:
                        float_prices = [float(p) for p in prices]
                        buy = max(float_prices)
                        sell = min(float_prices)
                        logger.info("Dadeforex: buy={}, sell={}".format(buy, sell))
                        return {'AUD_CNY': {'buy': buy, 'sell': sell}}
            
            # 备选：查找表格
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td'])
                    if len(cells) >= 2:
                        prices = [c.get_text().strip() for c in cells if re.match(r'^4\.\d{4}$', c.get_text().strip())]
                        if len(prices) >= 2:
                            float_prices = [float(p) for p in prices]
                            buy = max(float_prices)
                            sell = min(float_prices)
                            return {'AUD_CNY': {'buy': buy, 'sell': sell}}
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error("Dadeforex error: {}".format(e))
            return {'AUD_CNY': {'buy': None, 'sell': None}}

    def scrape_gtrading(self):
        """抓取GTrading的汇率"""
        try:
            url = self.companies['gtrading']
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            import re
            
            tables = soup.find_all('table')
            for table in tables:
                headers = [th.get_text().strip() for th in table.find_all('th')]
                buy_idx = sell_idx = None
                
                for i, h in enumerate(headers):
                    if '现汇买' in h or 'WE SELL TT' in h.upper():
                        buy_idx = i
                    if '现汇卖' in h or 'WE BUY TT' in h.upper():
                        sell_idx = i
                
                if buy_idx is not None and sell_idx is not None:
                    for row in table.find_all('tr'):
                        cells = row.find_all(['td', 'th'])
                        joined = ' '.join([c.get_text().strip() for c in cells])
                        if '澳元' in joined and '人民币' in joined:
                            try:
                                buy = float(cells[buy_idx].get_text().strip())
                                sell = float(cells[sell_idx].get_text().strip())
                                if buy and sell:
                                    logger.info("GTrading: buy={}, sell={}".format(buy, sell))
                                    return {'AUD_CNY': {'buy': buy, 'sell': sell}}
                            except:
                                continue
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error("GTrading error: {}".format(e))
            return {'AUD_CNY': {'buy': None, 'sell': None}}

    def scrape_kundaxpay(self):
        """抓取Kundaxpay的汇率"""
        try:
            url = self.companies['kundaxpay']
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            import re
            
            # 查找表格
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td'])
                    if len(cells) >= 5:
                        cell_texts = [c.get_text().strip() for c in cells]
                        row_text = row.get_text()
                        
                        if ('AUD' in row_text or 'CNY' in row_text or '澳元' in row_text) and len(cell_texts) >= 5:
                            # cells[3] 和 cells[4] 应该是买入价和卖出价
                            prices = [c for c in cell_texts if re.match(r'^4\.\d{4}$', c)]
                            if len(prices) >= 2:
                                float_prices = [float(p) for p in prices]
                                buy = max(float_prices)
                                sell = min(float_prices)
                                logger.info("Kundaxpay: buy={}, sell={}".format(buy, sell))
                                return {'AUD_CNY': {'buy': buy, 'sell': sell}}
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error("Kundaxpay error: {}".format(e))
            return {'AUD_CNY': {'buy': None, 'sell': None}}

    def scrape_all_companies(self):
        """串行抓取所有公司的汇率"""
        all_rates = {}
        
        scrapers = [
            ('moneychain', self.scrape_moneychain),
            ('supay', self.scrape_supay),
            ('moneychase', self.scrape_moneychase),
            ('dadeforex', self.scrape_dadeforex),
            ('gtrading', self.scrape_gtrading),
            ('kundaxpay', self.scrape_kundaxpay)
        ]
        
        for name, scraper in scrapers:
            try:
                logger.info("Scraping {}...".format(name))
                rates = scraper()
                if rates:
                    all_rates[name] = rates
                # 强制垃圾回收
                gc.collect()
                time.sleep(1)  # 避免请求过快
            except Exception as e:
                logger.error("Error scraping {}: {}".format(name, e))
        
        # 添加时间戳
        all_rates['timestamp'] = datetime.now().isoformat()
        
        return all_rates

    def save_rates(self, rates, filename='exchange_rates.json'):
        """保存汇率数据到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(rates, f, indent=2, ensure_ascii=False)
            logger.info("Rates saved to {}".format(filename))
        except Exception as e:
            logger.error("Error saving rates: {}".format(e))

if __name__ == "__main__":
    scraper = ExchangeRateScraper()
    rates = scraper.scrape_all_companies()
    print(json.dumps(rates, indent=2, ensure_ascii=False))
    scraper.save_rates(rates)
