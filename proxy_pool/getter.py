import re

from .utils import get_html
from .db import formproxy

def routes():
    routes = [
        ('https://www.kuaidaili.com/free/inha/1/', crawl_kuaidaili),
        ('http://www.data5u.com/free/gngn/index.shtml', crawl_data5u),
        ('http://www.ip3366.net/free/?stype=1&page=1', crawl_ip3366),
        (['http://www.qydaili.com/free/?action=china&page=%d' % x for x in range(1, 5)], crawl_qydaili),
    ]
    return routes

def crawl_kuaidaili(url):
    '''快代理'''
    r = get_html(url)
    if not r:
        return
    proxies = re.findall(r'<td data-title="IP">(.*?)</td>\s*' # 地址
                         r'<td data-title="PORT">(\d+)</td>\s*' # 端口
                         r'<td data-title="匿名度">高匿名</td>\s*'
                         r'<td data-title="类型">(\w+)</td>', # 类型
                         r.text)
    for adress, port, iptype in proxies:
        result = adress + ':' + port
        yield formproxy(iptype, result)

def crawl_data5u(url):
    '''无忧代理'''
    r = get_html(url)
    if not r:
        return
    proxies = re.findall(r'<span><li>(.*?)</li></span>\s*' # 地址
                    r'<span style="width: 100px;"><li class="port \w+">(\d+)</li></span>\s*' # 端口
                    r'<span style="width: 100px; color:red;"><li>高匿</li></span>\s*' # 匿名
                    r'<span style="width: 100px;"><li>(\w+)</li></span>', # 种类
                         r.text)
    for adress, port, iptype in proxies:
        result = adress + ':' + port
        yield formproxy(iptype, result)

def crawl_ip3366(url):
    '''云代理'''
    r = get_html(url)
    if not r:
        return
    proxies = re.findall(r'<td>(.*?)</td>\s*<td>(\w+)</td>\s*<td>高匿代理IP</td>\s*<td>(\w+)</td>',
                         r.content.decode('gb2312'))
    for addr, port, iptype in proxies:
        result = '%s:%s' %(addr, port)
        yield formproxy(iptype, result)

def crawl_qydaili(urls):
    '''旗云代理'''
    for url in urls:
        r = get_html(url)
        if not r:
            continue
        proxies = re.findall(r'<td data-title="IP">(.*?)</td>\s*'
                        r'<td data-title="PORT">(\w+)</td>\s*'
                        r'<td data-title="匿名度">高匿</td>\s*'
                        r'<td data-title="类型">(.*?)</td>', r.text)
        for addr, port, iptype in proxies:
            result = '%s:%s' %(addr, port)
            yield formproxy(iptype, result)