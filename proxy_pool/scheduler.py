import time
from .getter import routes
from .checker import ProxyChecker
from .settings import LOWER_LIMIT, UPPER_LIMIT
from .proxy import ProxyCrawler, Proxy
from .utils import get_logger

logger = get_logger(__name__)

class ProxyScheduler(Proxy):
    '''调度器'''
    @classmethod
    def get_proxy(cls, interval=5):
        while True:
            logger.info('Now valid proxies count is {}'.format(cls.sql.length))
            if cls.sql.length < UPPER_LIMIT:
                for route in routes():
                    crawler = ProxyCrawler(route)
                    crawler.run()
            else:
                time.sleep(interval)

    @classmethod
    def check_proxy(cls, interval=5):
        checker = ProxyChecker()
        while True:
            logger.info('Now raw proxies count is {}'.format(cls.sql.raw_length))
            if cls.sql.raw_length != 0:
                count = 10 if cls.sql.raw_length > 10 else cls.sql.raw_length
                if count == 1:
                    proxy = cls.sql.get_raw()
                    checker.check_one(proxy)
                else:
                    checker.check_many(count=count)
            else:
                time.sleep(interval)