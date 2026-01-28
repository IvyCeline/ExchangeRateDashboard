import schedule
import time
from datetime import datetime, timedelta
from exchange_scraper import ExchangeRateScraper
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RateScheduler:
    def __init__(self):
        self.scraper = ExchangeRateScraper()

    def is_business_hours(self):
        """检查是否在营业时间内（上午10点到下午6点）"""
        now = datetime.now()
        current_hour = now.hour
        # 营业时间：上午10点到下午6点
        return 10 <= current_hour < 18

    def update_rates(self):
        """更新汇率数据"""
        if not self.is_business_hours():
            logger.info("当前不在营业时间内，跳过更新")
            return

        logger.info("开始更新汇率数据...")
        try:
            rates = self.scraper.scrape_all_companies()
            self.scraper.save_rates(rates)
            logger.info("汇率数据更新完成")

            # 打印当前汇率摘要
            for company, company_rates in rates.items():
                if company != 'timestamp' and company_rates.get('AUD_CNY'):
                    aud_cny = company_rates['AUD_CNY']
                    buy = aud_cny.get('buy', 'N/A')
                    sell = aud_cny.get('sell', 'N/A')
                    logger.info(f"{company}: AUD/CNY 买入={buy}, 卖出={sell}")

        except Exception as e:
            logger.error(f"更新汇率数据时出错: {e}")

    def start_scheduler(self):
        """启动调度器"""
        logger.info("启动汇率更新调度器...")

        # 每10秒执行一次（实时更新模式）
        schedule.every(10).seconds.do(self.update_rates)

        # 立即执行一次
        self.update_rates()

        logger.info("调度器已启动，每10秒更新一次汇率数据")

        while True:
            schedule.run_pending()
            time.sleep(1)  # 每秒检查一次是否有任务需要执行

if __name__ == "__main__":
    scheduler = RateScheduler()
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        logger.info("调度器已停止")
    except Exception as e:
        logger.error(f"调度器运行出错: {e}")

