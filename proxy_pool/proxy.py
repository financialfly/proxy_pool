'''
proxy
'''
from .utils import get_logger
from .db import ProxySql

class Proxy(object):
    '''基类'''
    sql = ProxySql()

    @property
    def logger(self):
        return get_logger(self.__class__.__name__.lower().replace('proxy', ''))

from threading import Thread
class ProxyCrawler(Thread, Proxy):
    '''用于封装代理爬虫的多线程类'''
    def __init__(self, crawler_route, *args, **kwargs):
        # ex. ('https://www.kuaidaili.com/free/inha/1/', self.crawl_kuaidaili)
        self.url, self.func = crawler_route
        self.proxies = list()
        super().__init__(*args, **kwargs)

    def run(self):
        for proxy in self.func(self.url):
            self.logger.info('Got raw proxy %s' % proxy)
            self.proxies.append(proxy)
        self.sql.put_many(self.proxies)
        self.logger.info('Raw proxies saved.')

    @property
    def logger(self):
        return get_logger(self.func.__name__)