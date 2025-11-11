from __future__ import annotations
import logging

from twisted.internet import task

from scrapy import signals
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)


class LogStats:
    """Log basic scraping stats periodically"""

    def __init__(self, stats, interval=60.0):
        self.stats = stats
        self.interval = interval
        self.multiplier = 60.0 / self.interval
        self.task = None

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getfloat("LOGSTATS_INTERVAL")
        if not interval:
            raise NotConfigured
        o = cls(crawler.stats, interval)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.pagesprev = 0
        self.itemsprev = 0

        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)

    def log(self, spider):
        items = self.stats.get_value("item_scraped_count", 0)
        pages = self.stats.get_value("response_received_count", 0)
        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        self.pagesprev, self.itemsprev = pages, items

        msg = (
            "Crawled %(pages)d pages (at %(pagerate)d pages/min), "
            "scraped %(items)d items (at %(itemrate)d items/min)"
        )
        log_args = {
            "pages": pages,
            "pagerate": prate,
            "items": items,
            "itemrate": irate,
        }
        logger.info(msg, log_args, extra={"spider": spider})

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()
        rpm_final, ipm_final = self.calculate_final_stats(spider)
        self.stats.set_value("responses_per_minute", rpm_final)
        self.stats.set_value("items_per_minute", ipm_final)

    def calculate_final_stats(
        self, spider
    ) -> tuple[None, None] | tuple[float, float]:
        start_time = self.stats.get_value("start_time")
        finish_time = self.stats.get_value("finish_time")

        if not start_time or not finish_time:
            return None, None

        mins_elapsed = (finish_time - start_time).seconds / 60

        if mins_elapsed == 0:
            return None, None

        items = self.stats.get_value("item_scraped_count", 0)
        pages = self.stats.get_value("response_received_count", 0)

        return (pages / mins_elapsed), (items / mins_elapsed)
