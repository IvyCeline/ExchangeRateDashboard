    def scrape_kundaxpay(self):
        """抓取Kundaxpay的汇率 - 使用Playwright渲染动态页面"""
        try:
            url = self.companies['kundaxpay']
            
            # 使用Playwright渲染动态内容
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=60000)
                
                # 等待更长时间确保动态内容完全加载
                page.wait_for_timeout(10000)
                
                # 查找包含 AUD CNY 的行并提取最后两个数字（现汇买入/卖出价）
                result = page.evaluate('''() => {
                    const allText = document.body.innerText;
                    const lines = allText.split('\\n');
                    
                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i].trim();
                        // 找到包含 AUD 和 CNY 的行
                        if ((line.includes('AUD') || line.includes('CNY')) && 
                            lines[i+1] && (lines[i+1].includes('AUD') || lines[i+1].includes('CNY'))) {
                            
                            // 收集该行及后续几行中的所有4位小数数字
                            let allNumbers = [];
                            for (let j = i; j < lines.length; j++) {
                                const nums = lines[j].match(/4\\.\\d{4}/g);
                                if (nums) {
                                    allNumbers = allNumbers.concat(nums);
                                }
                                // 如果已经找到至少4个数字就停止
                                if (allNumbers.length >= 4) break;
                            }
                            
                            if (allNumbers.length >= 4) {
                                // 最后两个是现汇买入/卖出价
                                return {
                                    buy: allNumbers[allNumbers.length - 2],
                                    sell: allNumbers[allNumbers.length - 1]
                                };
                            }
                        }
                    }
                    return null;
                }''')
                
                browser.close()
                
                if result and result.get('buy') and result.get('sell'):
                    try:
                        buy = float(result['buy'])
                        sell = float(result['sell'])
                        logger.info(f"Kundaxpay: buy={buy}, sell={sell}")
                        return {'AUD_CNY': {'buy': buy, 'sell': sell}}
                    except (ValueError, TypeError) as e:
                        logger.error(f"Kundaxpay: Failed to parse numbers: {e}")
                        
            logger.warning("Kundaxpay: Could not find AUD/CNY data")
            return {'AUD_CNY': {'buy': None, 'sell': None}}
        except Exception as e:
            logger.error(f"Error scraping Kundaxpay: {e}")
            return None

