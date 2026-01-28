"""
Fix scrape_gtrading function in exchange_scraper.py
"""
import re

# Read the original file
with open('exchange_scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

# New scrape_gtrading function
new_function = '''    def scrape_gtrading(self):
        """抓取GTrading的汇率"""
        try:
            url = self.companies['gtrading']
            
            # 使用 Playwright 直接解析渲染后的页面
            def parse_with_playwright(url):
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    page.wait_for_timeout(3000)
                    
                    result = page.evaluate('''
                        () => {
                            const tables = document.querySelectorAll('table');
                            for (let table of tables) {
                                const ths = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
                                
                                // 查找现汇买入价和现汇卖出价的索引
                                let buy_idx = -1, sell_idx = -1;
                                for (let i = 0; i < ths.length; i++) {
                                    const h = ths[i];
                                    if (h.includes('现汇买入价') || h.includes('现汇买入')) {
                                        buy_idx = i;
                                    }
                                    if (h.includes('现汇卖出价') || h.includes('现汇卖出')) {
                                        sell_idx = i;
                                    }
                                }
                                
                                // 如果找到了正确的列索引，查找 AUD/CNY 行
                                if (buy_idx >= 0 && sell_idx >= 0) {
                                    const rows = table.querySelectorAll('tbody tr');
                                    for (let row of rows) {
                                        const cells = Array.from(row.querySelectorAll('td')).map(td => td.innerText.trim());
                                        const row_text = row.innerText || '';
                                        
                                        // 查找包含澳元和人民币的行
                                        if ((row_text.includes('澳元') && row_text.includes('人民币')) ||
                                            (row_text.includes('AUD') && row_text.includes('CNY'))) {
                                            
                                            const buy = cells[buy_idx];
                                            const sell = cells[sell_idx];
                                            
                                            // 验证是否为有效的汇率数字
                                            if (/^4\\\\.\\\\d{4}$/.test(buy) && /^4\\\\.\\\\d{4}$/.test(sell)) {
                                                return {
                                                    found: true,
                                                    buy: parseFloat(buy),
                                                    sell: parseFloat(sell),
                                                    row_text: row_text.substring(0, 100)
                                                };
                                            }
                                        }
                                    }
                                }
                            }
                            return {found: false};
                        }
                    ''')
                    
                    browser.close()
                    return result
            
            result = parse_with_playwright(url)
            
            if result and result.get('found'):
                logger.info("GTrading: buy={}, sell={}".format(result['buy'], result['sell']))
                return {'AUD_CNY': {'buy': result['buy'], 'sell': result['sell']}}
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}
            
        except Exception as e:
            logger.error("Error scraping GTrading: {}".format(e))
            return None

'''

# Find and replace the old function
# Pattern to match from "def scrape_gtrading" to "def scrape_kundaxpay"
pattern = r'    def scrape_gtrading\(self\):.*?(?=    def scrape_kundaxpay)'

match = re.search(pattern, content, re.DOTALL)

if match:
    print("Found scrape_gtrading function, replacing...")
    new_content = content[:match.start()] + new_function + content[match.end():]
    
    with open('exchange_scraper.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Successfully replaced scrape_gtrading function!")
else:
    print("Could not find scrape_gtrading function to replace")






