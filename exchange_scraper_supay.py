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
                                    
                                    // 查找 4.xxxx 格式的价格
                                    const prices = cells.filter(t => /^4\\.\\d{4}$/.test(t));
                                    
                                    // VIP 行通常有两个价格: AskTT(卖出价) 和 BidTT(买入价)
                                    if (prices.length >= 2) {
                                        return {
                                            found: true,
                                            type: 'vip',
                                            sell: prices[0],  // AskTT - 卖出价
                                            buy: prices[1],   // BidTT - 买入价
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
                                    
                                    if (all_prices.length >= 2) {
                                        return {
                                            found: true,
                                            type: 'regular',
                                            sell: all_prices[0],
                                            buy: all_prices[1],
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
                    sell = float(result['sell'])
                    buy = float(result['buy'])
                    logger.info(f"Supay: VIP row found - buy={buy}, sell={sell}")
                    return {'AUD_CNY': {'buy': buy, 'sell': sell}}
                except (ValueError, KeyError) as e:
                    logger.error(f"Supay: Failed to parse prices: {e}")
            
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
                                    return {'AUD_CNY': {'buy': float(prices[1]), 'sell': float(prices[0])}}
            except Exception as e:
                logger.error(f"Supay fallback requests failed: {e}")
            
            return {'AUD_CNY': {'buy': None, 'sell': None}}

        except Exception as e:
            logger.error(f"Error scraping Supay: {e}")
            return None

    def scrape_moneychase(self):





