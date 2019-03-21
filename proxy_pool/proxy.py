'''
proxy
'''
from .utils import get_logger
from .db import ProxySql

class Proxy(object):
    '''基类'''
    @property
    def logger(self):
        return get_logger(self.__class__.__name__.lower().replace('proxy', ''))

    @property
    def sql(self):
        return ProxySql()


from threading import Thread
class ProxyCrawler(Thread, Proxy):
    '''用于封装代理爬虫的多线程类'''
    def __init__(self, crawl_func, *args, **kwargs):
        self.func = crawl_func
        self.proxies = list()
        super().__init__(*args, **kwargs)

    def run(self):
        for proxy in self.func():
            self.logger.debug('Got raw proxy %s' % proxy)
            self.proxies.append(proxy)
        self.sql.put_many(self.proxies)

    @property
    def logger(self):
        return get_logger(self.func.__name__)