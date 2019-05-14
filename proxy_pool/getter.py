import re

from .utils import get_html
from .proxy import Proxy
from .db import formproxy

class ProxyGetter(Proxy):

    def routes(self):
        routes = [
            ('https://www.kuaidaili.com/free/inha/1/', self.crawl_kuaidaili),
            ('http://www.data5u.com/free/gngn/index.shtml', self.crawl_data5u),
            ('http://www.ip3366.net/free/?stype=1&page=1', self.crawl_ip3366),
            (['http://www.qydaili.com/free/?action=china&page=%d' % x for x in range(1, 5)], self.crawl_qydaili)
        ]
        return routes

    @classmethod
    def get_crawl_routes(cls):
        g = cls()
        return g.routes()

    def crawl_kuaidaili(self, url):
        '''快代理'''
        r = get_html(url)
        if r:
            ip = re.compile(r'td data-title="IP">(.*?)</td>\s*<td data-title="PORT">(\w+)</td>\s*<td data-title="匿名度">(.*?)</td>\s*<td data-title="类型">(.*?)</td>')
            iplist = ip.findall(r.text)
            for adress, port, anonymity, iptype in iplist:
                if not anonymity == '高匿名':
                    continue
                result = adress + ':' + port
                yield formproxy(iptype, result)

    def crawl_data5u(self, url):
        '''无忧代理'''
        r = get_html(url)
        ip = re.compile(r'<span><li>(.*?)</li></span>\s*' # 地址
                        r'<span style="width: 100px;"><li class="port \w+">(\d+)</li></span>\s*' # 端口
                        r'<span style="width: 100px; color:red;"><li>高匿</li></span>\s*' # 匿名
                        r'<span style="width: 100px;"><li>(\w+)</li></span>') # 种类
        iplist = ip.findall(r.text)
        for adress, port, iptype in iplist:
            result = adress + ':' + port
            yield formproxy(iptype, result)

    def crawl_ip3366(self, url):
        '''云代理'''
        r = get_html(url)
        if r:
            ip = re.compile(r'<td>(.*?)</td>\s*<td>(\w+)</td>\s*<td>(.*?)</td>\s*<td>(\w+)</td>')
            iplist = ip.findall(r.content.decode('gb2312'))
            for addr, port, anonymity, iptype in iplist:
                if not anonymity.startswith('高匿'):
                    continue
                result = '%s:%s' %(addr, port)
                yield formproxy(iptype, result)

    def crawl_qydaili(self, urls):
        '''旗云代理'''
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