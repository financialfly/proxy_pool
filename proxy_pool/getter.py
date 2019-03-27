import re

from .utils import get_html
from .proxy import Proxy
from .db import formproxy

class ProxyGetter(Proxy):

    def __init__(self):
        # 获取所有爬虫函数，此时crawlers还没有被创建所以获取不到它本身
        self.crawlers = [x for x in dir(self) if 'crawl' in x]

    def crawl_kuaidaili(self):
        '''快代理'''
        url = 'https://www.kuaidaili.com/free/inha/1/'
        r = get_html(url)
        if r:
            ip = re.compile(r'td data-title="IP">(.*?)</td>\s*<td data-title="PORT">(\w+)</td>\s*<td data-title="匿名度">(.*?)</td>\s*<td data-title="类型">(.*?)</td>')
            iplist = ip.findall(r.text)
            for adress, port, anonymity, iptype in iplist:
                if not anonymity == '高匿名':
                    continue
                result = adress + ':' + port
                yield formproxy(iptype, result)

    def crawl_data5u(self):
        '''无忧代理'''
        url = 'http://www.data5u.com/free/gngn/index.shtml'
        r = get_html(url)
        ip = re.compile(r'<span><li>(.*?)</li></span>\s*<span.*?class="port GEGEA">(\w+)</li></span>\s*<span.*?><li>(.*?)</li></span>\s*<span.*?><li>(.*?)</li></span>')
        iplist = ip.findall(r.text)
        for adress, port, anonymity, iptype in iplist:
            if not anonymity == '高匿':
                continue
            result = adress + ':' + port
            yield formproxy(iptype, result)

    def crawl_ip3366(self):
        '''云代理'''
        url = 'http://www.ip3366.net/free/?stype=1&page=1'
        r = get_html(url)
        if r:
            ip = re.compile(r'<td>(.*?)</td>\s*<td>(\w+)</td>\s*<td>(.*?)</td>\s*<td>(\w+)</td>')
            iplist = ip.findall(r.content.decode('gb2312'))
            for addr, port, anonymity, iptype in iplist:
                if not anonymity.startswith('高匿'):
                    continue
                result = '%s:%s' %(addr, port)
                yield formproxy(iptype, result)

    def crawl_qydaili(self):
        '''旗云代理'''
        urls = ['http://www.qydaili.com/free/?action=china&page=%d' % x for x in range(1, 5)]
        for url in urls:
            r = get_html(url)
            if r:
                ip = re.compile(r'<td data-title="IP">(.*?)</td>\s*<td data-title="PORT">(\w+)</td>\s*<td data-title="匿名度">(.*?)</td>\s*<td data-title="类型">(.*?)</td>')
                iplist = ip.findall(r.text)
                for addr, port, anonymity, iptype in iplist:
                    if not anonymity == '高匿':
                        continue
                    result = '%s:%s' %(addr, port)
                    yield formproxy(iptype, result)

def crawl_funcs():
    '''获取爬虫函数'''
    g = ProxyGetter()
    funcs = [getattr(g, f) for f in g.crawlers]
    return funcs