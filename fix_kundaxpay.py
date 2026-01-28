    def scrape_kundaxpay(self):
        """抓取Kundaxpay的汇率 - 精确提取现汇买入/卖出价"""
        try:
            url = self.companies['kundaxpay']
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=60000)
                page.wait_for_timeout(5000)
                
                # 直接查询表格中的 AUD/CNY 行
                result = page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('tr');
                        for (let row of rows) {
                            const cells = Array.from(row.querySelectorAll('td')).map(td => td.innerText.trim());
                            const rowText = row.innerText || '';
                            
                            // 查找 AUD CNY 行
                            if ((rowText.includes('AUD') || rowText.includes('CNY')) && cells.length >= 5) {
                                // cells[0] = AUD/CNY, cells[3] = 现汇买入价, cells[4] = 现汇卖出价
                                const buy = cells[3];
                                const sell = cells[4];
                                
                                // 验证是否为有效汇率格式 4.xxxx
                                if (/^4\\.\\d{4}$/.test(buy) && /^4\\.\\d{4}$/.test(sell)) {
                                    return {
                                        found: true,
                                        buy: buy,
                                        sell: sell,
                                        allCells: cells
                                    };
                                }
                            }
                        }
                        return {found: false};
                    }
                """)
                
                browser.close()
                
                if result and result.get('found'):
                    try:
                        buy = float(result['buy'])
                        sell = float(result['sell'])
                        logger.info("Kundaxpay: buy={}, sell={}".format(buy, sell))
                        return {'AUD_CNY': {'buy': buy, 'sell': sell}}
                    except (ValueError, TypeError) as e:
                        logger.error("Kundaxpay: Failed to parse numbers: {}".format(e))
                
            logger.warning("Kundaxpay: Could not find AUD/CNY data")
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error("Error scraping Kundaxpay: {}".format(e))
            return None






