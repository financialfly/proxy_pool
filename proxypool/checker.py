import re

from .db import DbClient
from .utils import get_logger
from .request import Request, Crawler

logger = get_logger('Checker')

class ProxyChecker(object):
    '''检查代理是否可用'''

    def __init__(self):
        self.httpsurl = 'https://httpbin.org/ip'
        self.httpurl = 'http://2019.ip138.com/ic.asp'
        self.crawler = Crawler(requests=list(), logger=logger)
        self.sql = DbClient()

    def check_http(self, response):
        proxy = response.meta['proxy']
        if response.status_code == 200 and response.text:
            current_ip = re.search(r'您的IP是：\[(.*?)\]', response.content.decode('gb2312')).group(1)
            logger.debug('Current ip is %s' % current_ip)
            self.process_result(proxy)
        else:
            self.process_result(proxy, is_useful=False)

    def check_https(self, response):
        proxy = response.meta['proxy']
        if response.status_code == 200 and response.text:
            current_ip = response.json()['origin']
            logger.debug('Current ip is %s' % current_ip)
            self.process_result(proxy)
        else:
            self.process_result(proxy, is_useful=False)

    def process_result(self, proxy, is_useful=True):
       '''处理检查的结果'''
       if is_useful:
           self.sql.update_useful(proxy)
           logger.info('Got valid proxy %s' % proxy)
       else:
           logger.debug('invalid proxy %s' % proxy)
           self.sql.delete(proxy)

    def check(self, count=10):
        self._update_reqs(iptype='http', count=count)
        self._update_reqs(iptype='https', count=count)
        if self.crawler.requests:
            self.crawler.run()

    def _update_reqs(self, iptype, count):
        if iptype == 'http':
            url = self.httpurl
            callback = self.check_http
        else:
            url = self.httpsurl
            callback = self.check_https
        http_proxies = self.sql.get_raw(count=count, iptype=iptype)
        if http_proxies:
            http_reqs = [Request(url=url,
                                 callback=callback,
                                 meta={'proxy': proxy},
                                 retry_times=0,
                                 proxies=proxy.dict()) for proxy in http_proxies]
            self.crawler.requests.extend(http_reqs)