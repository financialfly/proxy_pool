import asyncio

from .utils import get_html
from .proxy import Proxy
from functools import partial

class ProxyChecker(Proxy):

    def __init__(self):
        self.url = 'https://httpbin.org/ip'
        super().__init__()

    async def _check(self, proxy):
        _proxy = self.get_proxy(proxy)
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, partial(get_html, self.url, proxies=_proxy, retry_time=1, timeout=5))
        r = await future
        if r.status_code == 200:
            result = r.json()
            self.logger.debug('current ip is %s' % result['origin'])
            self.sql.update_useful(proxy)
            self.logger.info('Got valid proxy %s' % proxy)
        else:
            self.logger.debug('invalid proxy %s' % proxy)
            self.sql.delete(proxy)

    def get_proxy(self, proxy):
        return {'https': proxy}

    def _run(self, proxy=None, proxies=None):
        if proxy and proxies:
            self.logger.warning('Only one argument will be accept')

        event_loop = asyncio.get_event_loop()
        if proxies:
            tasks = [self._check(proxy) for proxy in proxies]
            event_loop.run_until_complete(asyncio.gather(*tasks))
        elif proxy:
            event_loop.run_until_complete(self._check(proxy))

    def check_many(self, count=10):
        proxies = self.sql.get_raw(count=count)
        self._run(proxies=proxies)

    def check_one(self, proxy=None):
        _proxy = proxy or self.sql.get_raw()
        self._run(proxy=_proxy)