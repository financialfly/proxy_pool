import re

from lxml import etree
from utils import get_html
from _proxy import Proxy

class ProxyGetter(Proxy):

    def __init__(self):
        # 获取所有爬虫函数，此时crawlers还没有被创建所以获取不到它本身
        self.crawlers = [x for x in dir(self) if 'crawl' in x]

    def crawl_kuaidaili(self):
        url = 'https://www.kuaidaili.com/free/inha/1/'
        r = get_html(url)
        if r:
            ip_adress = re.compile(
                '<td data-title="IP">(.*)</td>\s*<td data-title="PORT">(\w+)</td>'
            )
            re_ip_adress = ip_adress.findall(r.text)
            for adress, port in re_ip_adress:
                result = adress + ':' + port
                yield result.replace(' ', '')

    def crawl_data5u(self):
        url = 'http://www.data5u.com/free/gngn/index.shtml'
        r = get_html(url)
        ip_adress = re.compile(
            ' <ul class="l2">\s*<span><li>(.*?)</li></span>\s*<span style="width: 100px;"><li class=".*">(.*?)</li></span>'
        )
        # \s * 匹配空格，起到换行作用
        re_ip_adress = ip_adress.findall(r.text)
        for adress, port in re_ip_adress:
            result = adress + ':' + port
            yield result.replace(' ', '')

    def crawl_ip3366(self):
        url = 'http://www.ip3366.net/free/?stype=1&page=1'
        r = get_html(url)
        html = etree.HTML(r.text)
        trs = html.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr')
        for tr in trs:
            ip_addr = tr.xpath('.//td[1]/text()')[0]
            ip_port = tr.xpath('.//td[2]/text()')[0]
            full_ip = ip_addr + ':' + ip_port
            yield full_ip.replace(' ','')

    def crawl_qydaili(self):
        '''旗云代理'''
        urls = ['http://www.qydaili.com/free/?action=china&page=%d' % x for x in range(1, 5)]
        for url in urls:
            r = get_html(url)
            addrs = re.findall(r'data-title="IP">(.*?)</td>', r.text)
            ports = re.findall(r'data-title="PORT">(\d+)</td>', r.text)
            for a, p in zip(addrs, ports):
                proxy = '%s:%s' %(a, p)
                yield proxy

def crawl_funcs():
    '''获取爬虫函数'''
    g = ProxyGetter()
    funcs = [getattr(g, f) for f in g.crawlers]
    return funcs