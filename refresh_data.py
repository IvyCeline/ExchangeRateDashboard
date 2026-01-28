"""
Refresh all data
"""
from exchange_scraper import ExchangeRateScraper

scraper = ExchangeRateScraper()

# Rescrape all data
result = scraper.scrape_all_companies()
scraper.save_rates(result)

print('All data saved:')
for company, data in result.items():
    if company != 'timestamp' and data.get('AUD_CNY'):
        print('{}: buy={}, sell={}'.format(company, data['AUD_CNY']['buy'], data['AUD_CNY']['sell']))






