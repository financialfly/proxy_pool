import re
import logging

from async_request import Crawler, Request
from proxypool.db import DbClient
from proxypool.proxy import formproxy

logger = logging.getLogger('ProxyPool-Crawler')
logging.basicConfig(level=logging.INFO)


class ProxyCrawler:

    url_with_parse_func = [
        ('https://www.kuaidaili.com/free/inha/1/', 'parse_kuaidaili'),
        ('http://www.data5u.com/free/gngn/index.shtml', 'parse_data5u'),
        ('http://www.ip3366.net/free/?stype=1&page=1', 'parse_ip3366'),
        ('http://www.qydaili.com/free/?action=china&page=1', 'parse_qydaili'),
        ('https://www.xicidaili.com/nn/', 'parse_xici')
    ]
    checks = {
        'http': ('https://httpbin.org/ip', 'check_http'),
        'https': ('https://httpbin.org/ip', 'check_https'),
    }

    def __init__(self):
        self.db = DbClient()
        self.crawler = Crawler(result_back=self.process_proxy, max_retries=0)
        self.seen_proxy = set()

    def __del__(self):
        self.db.close()

    def start_request(self):
        for url, parse_func in self.url_with_parse_func:
            func = getattr(self, parse_func)
            req = Request(url, verify=False, callback=func)
            self.crawler.add_request(req)
            logger.info(f'Crawling {req}')
        self.crawler.run()

    def process_proxy(self, proxy):
        if proxy.addr in self.seen_proxy:
            logger.info(f'Filtered seen proxy {proxy}')
            return
        self.seen_proxy.add(proxy.addr)
        url, func = self.checks[proxy.type]
        func = getattr(self, func)
        req = Request(url, callback=func, meta={'proxy': proxy}, proxies=proxy.dict())
        self.crawler.add_request(req)

    def check_http(self, response):
        proxy = response.meta['proxy']
        if response.status_code == 200:
            self.process_checked_proxy(proxy)

    def check_https(self, response):
        proxy = response.meta['proxy']
        if response.status_code == 200 and response.text:
            current_ip = response.json()['origin']
            logger.debug('Current ip is %s' % current_ip)
            self.process_checked_proxy(proxy)

    def process_checked_proxy(self, proxy):
        logger.info(f'Got useful proxy: {proxy}')
        proxy.status = 1
        self.db.put(proxy)

    def parse_kuaidaili(self, response):
        '''快代理'''
        proxies = re.findall(r'<td data-title="IP">(.*?)</td>\s*'  # 地址
                             r'<td data-title="PORT">(\d+)</td>\s*'  # 端口
                             r'<td data-title="匿名度">高匿名</td>\s*'
                             r'<td data-title="类型">(\w+)</td>',  # 类型
                             response.text)
        return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

    def parse_data5u(self, response):
        '''无忧代理'''
        proxies = re.findall(r'<span><li>(.*?)</li></span>\s*'  # 地址
                             r'<span style="width: 100px;"><li class="port \w+">(\d+)</li></span>\s*'  # 端口
                             r'<span style="width: 100px; color:red;"><li>高匿</li></span>\s*'  # 匿名
                             r'<span style="width: 100px;"><li>(\w+)</li></span>',  # 种类
                             response.text)
        return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

    def parse_ip3366(self, response):
        '''云代理'''
        proxies = re.findall(r'<td>(.*?)</td>\s*<td>(\w+)</td>\s*<td>高匿代理IP</td>\s*<td>(\w+)</td>',
                             response.content.decode('gb2312'))
        return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

    def parse_qydaili(self, response):
        '''旗云代理'''
        proxies = re.findall(r'<td data-title="IP">(.*?)</td>\s*'
                             r'<td data-title="PORT">(\w+)</td>\s*'
                             r'<td data-title="匿名度">高匿</td>\s*'
                             r'<td data-title="类型">(.*?)</td>', response.text)
        return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

    def parse_66ip(self, response):
        proxies = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', response.text)
        return [formproxy('https', proxy) for proxy in proxies]

    def parse_xici(self, response):
        '''西刺代理'''
        proxies = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>\s*'  # ip
                             r'<td>(\d+)</td>\s*'  # port
                             r'<td>\s*<a .*?</a>\s*</td>\s*<td class="country">高匿</td>\s*'
                             r'<td>(\w+)</td>',  # type
                             response.text)
        return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]


if __name__ == '__main__':
    r = ProxyCrawler()
    r.start_request()