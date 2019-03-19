'''
proxy
'''
from utils import get_logger

class Proxy(object):
    '''基类'''

    @property
    def logger(self):
        return get_logger(__name__)


from threading import Thread
class ProxyCrawler(Thread):

    def __init__(self, crawl_func, db, *args, **kwargs):
        self.db = db
        self.func = crawl_func
        super().__init__(*args, **kwargs)

    def run(self):
        for proxy in self.func():
            self.logger.debug('Got proxy %s' % proxy)
            self.db.put(proxy)

    @property
    def logger(self):
        return get_logger('%s' % self.func.__name__.replace('crawl_', ''))