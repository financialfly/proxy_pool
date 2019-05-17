import async_request
import re

# from async_request.xpath import XpathSelector
from .db import DbClient
from .proxy import formproxy, ProxyCrawler
from .logs import get_logger

logger = get_logger('ProxyGetter')

class ProxyGetter(object):

    def __init__(self):
        self.db = DbClient()
        self.crawler = ProxyCrawler(requests=None, logger=logger, result_callback=self.process_proxy)

    @property
    def routes(self):
        routes = [
            # 地址 解析函数 参数(字典)
            ('https://www.kuaidaili.com/free/inha/1/', parse_kuaidaili, {'verify': False}),  # 快代理
            ('http://www.data5u.com/free/gngn/index.shtml', parse_data5u),  # 无忧代理
            ('http://www.ip3366.net/free/?stype=1&page=1', parse_ip3366),  # 云代理
            ('http://www.qydaili.com/free/?action=china&page=1', parse_qydaili),  # 旗云代理
            # ('http://www.66ip.cn/nmtq.php', parse_66ip, ip66_args()), # 代理66
            ('https://www.xicidaili.com/nn/', parse_xici, {'verify': False}) # 西刺代理
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
        reqs = list()
        for route in self.routes:
            if len(route) == 2:
                reqs.append(async_request.Request(url=route[0], callback=route[1]))
            elif len(route) == 3:
                reqs.append(async_request.Request(url=route[0], callback=route[1], **route[2]))
        self.crawler.requests = reqs
        self.crawler.run(close_eventloop=False)
        # self.crawler.run()

def parse_kuaidaili(response):
    '''快代理'''
    proxies = re.findall(r'<td data-title="IP">(.*?)</td>\s*' # 地址
                         r'<td data-title="PORT">(\d+)</td>\s*' # 端口
                         r'<td data-title="匿名度">高匿名</td>\s*'
                         r'<td data-title="类型">(\w+)</td>', # 类型
                         response.text)
    return [formproxy(iptype, '%s:%s' %(address, port)) for address, port, iptype in proxies]

def parse_data5u(response):
    '''无忧代理'''
    proxies = re.findall(r'<span><li>(.*?)</li></span>\s*' # 地址
                    r'<span style="width: 100px;"><li class="port \w+">(\d+)</li></span>\s*' # 端口
                    r'<span style="width: 100px; color:red;"><li>高匿</li></span>\s*' # 匿名
                    r'<span style="width: 100px;"><li>(\w+)</li></span>', # 种类
                         response.text)
    return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

def parse_ip3366(response):
    '''云代理'''
    proxies = re.findall(r'<td>(.*?)</td>\s*<td>(\w+)</td>\s*<td>高匿代理IP</td>\s*<td>(\w+)</td>',
                         response.content.decode('gb2312'))
    return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

def parse_qydaili(response):
    '''旗云代理'''
    proxies = re.findall(r'<td data-title="IP">(.*?)</td>\s*'
                    r'<td data-title="PORT">(\w+)</td>\s*'
                    r'<td data-title="匿名度">高匿</td>\s*'
                    r'<td data-title="类型">(.*?)</td>', response.text)
    return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]

def parse_66ip(response):
    proxies = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', response.text)
    return [formproxy('https', proxy) for proxy in proxies]

def ip66_args():
    cookies = {
        '__jsluid': '36c422bbb10e5ca2ecf66d0791b798bf',
        'Hm_lvt_1761fabf3c988e7f04bec51acd4073f4': '1558065500',
        '__jsl_clearance': '1558071288.482|0|7vNpPCJ8bzJu5zIbWYgoCRIt6%2B8%3D',
        'Hm_lpvt_1761fabf3c988e7f04bec51acd4073f4': '1558072117',
    }

    headers = {
        'Host': 'www.66ip.cn',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'http://www.66ip.cn/nm.html',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    }
    # proxytype 为1表示https，0表示http
    params = (
        ('getnum', '30'),
        ('isp', '0'),
        ('anonymoustype', '3'),
        ('start', ''),
        ('ports', ''),
        ('export', ''),
        ('ipaddress', ''),
        ('area', '0'),
        ('proxytype', '1'),
        ('api', '66ip'),
    )
    return {'cookies': cookies, 'headers': headers, 'params': params}

def parse_xici(response):
    '''西刺代理'''
    proxies = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>\s*' # ip
                         r'<td>(\d+)</td>\s*' # port
                         r'<td>\s*<a .*?</a>\s*</td>\s*<td class="country">高匿</td>\s*'
                         r'<td>(\w+)</td>', # type
                         response.text)
    return [formproxy(iptype, '%s:%s' % (address, port)) for address, port, iptype in proxies]