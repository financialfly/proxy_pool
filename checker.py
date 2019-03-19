from utils import get_html
from _proxy import Proxy

class ProxyChecker(Proxy):
    '''检查代理是否能用'''

    def __init__(self):
        self.url = 'https://httpbin.org/ip'
        self._proxy = None

    def check(self, proxy):
        self._proxy = proxy
        try:
            r = get_html(self.url, proxies=self.proxy, timeout=5)
        except Exception as e:
            self.logger.debug('invalid proxy %s (request error cause by %s)' % (self._proxy, e))
            return
        result = r.json()
        self.logger.debug('current ip is %s' % result['origin'])
        if self._proxy.split(':')[0] in result['origin']:
            self.logger.info('Got valid proxy %s' % self._proxy)
            return self._proxy
        else:
            self.logger.debug('invalid proxy %s' % self._proxy)

    @property
    def proxy(self):
        proxies = dict()
        proxies['http'] = 'http://%s' % self._proxy
        self.logger.debug('Got proxy %s' % proxies)
        return proxies

    def run(self):
        pass

def check_proxy(proxy):
    c = ProxyChecker()
    return c.check(proxy)