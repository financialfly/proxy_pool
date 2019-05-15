import re

from .db import DbClient
from .proxy import formproxy
from .request import Request, Crawler
from .logger import get_logger

logger = get_logger('ProxyGetter')

class ProxyGetter(object):

    def __init__(self):
        self.db = DbClient()
        self.crawler = Crawler(requests=None, logger=logger, result_callback=self.process_proxy)

    @property
    def routes(self):
        routes = [
            ('https://www.kuaidaili.com/free/inha/1/', crawl_kuaidaili),  # 快代理
            ('http://www.data5u.com/free/gngn/index.shtml', crawl_data5u),  # 无忧代理
            ('http://www.ip3366.net/free/?stype=1&page=1', crawl_ip3366),  # 云代理
            ('http://www.qydaili.com/free/?action=china&page=1', crawl_qydaili),  # 旗云代理
        ]
        return routes

    def process_proxy(self, proxy):
        '''处理结果'''
        logger.info('Got new proxies: {}'.format(proxy))
        if isinstance(proxy, list):
            self.db.put_many(proxy)
        else:
            self.db.put(proxy)

    def get(self):
        reqs = [Request(url=route[0], callback=route[1]) for route in self.routes]
        self.crawler.requests = reqs
        self.crawler.run()

def crawl_kuaidaili(response):
    '''快代理'''
    proxies = re.findall(r'<td data-title="IP">(.*?)</td>\s*' # 地址
                         r'<td data-title="PORT">(\d+)</td>\s*' # 端口
                         r'<td data-title="匿名度">高匿名</td>\s*'
                         r'<td data-title="类型">(\w+)</td>', # 类型
                         response.text)
    return [formproxy(iptype, '%s:%s' %(address, port)) for address, port, iptype in proxies]

def crawl_data5u(response):
    '''无忧代理'''
    proxies = re.findall(r'<span><li>(.*?)</li></span>\s*' # 地址
                    r'<span style="width: 100px;"><li class="port \w+">(\d+)</li></span>\s*' # 端口
                    r'<span style="width: 100px; color:red;"><li>高匿</li></span>\s*' # 匿名
                    r'<span style="width: 100px;"><li>(\w+)</li></span>', # 种类
                         response.text)
    return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

def crawl_ip3366(response):
    '''云代理'''
    proxies = re.findall(r'<td>(.*?)</td>\s*<td>(\w+)</td>\s*<td>高匿代理IP</td>\s*<td>(\w+)</td>',
                         response.content.decode('gb2312'))
    return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

def crawl_qydaili(response):
    '''旗云代理'''
    proxies = re.findall(r'<td data-title="IP">(.*?)</td>\s*'
                    r'<td data-title="PORT">(\w+)</td>\s*'
                    r'<td data-title="匿名度">高匿</td>\s*'
                    r'<td data-title="类型">(.*?)</td>', response.text)
    return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]