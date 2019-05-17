import async_request
import json
import requests
from functools import partial
from proxypool.logs import get_logger

class Proxy(object):
    '''代理'''
    __slots__ = ['type', 'addr']

    def __init__(self, iptype, ipaddr):
        self.type = iptype.lower()
        self.addr = ipaddr.strip()

    def json(self):
        return json.dumps({self.type: self.addr})

    def dict(self):
        return {self.type: self.addr}

    def __str__(self):
        return  '%s://%s' % (self.type, self.addr)

    __repr__ = __str__

def formproxy(iptype, ipaddr):
    return Proxy(iptype, ipaddr)



class ProxyCrawler(async_request.Crawler):
    '''
    基于async_request.Crawler定制的crawler类，主要便于实现多条代理直接存储
    '''
    def __init__(self, requests, result_callback=None, logger=None):
        super().__init__(requests, result_callback)
        if not logger:
            self.logger = get_logger('async_request.ProxyCrawler')
        else:
            self.logger = logger

    async def get_html(self, request):
        self.logger.debug('Crawling {}'.format(request.url))
        future = self.loop.run_in_executor(None, partial(requests.request, **request.params))
        while request.retry_times >= 0:
            try:
                response = await future
                break
            except Exception as e:
                self.logger.debug('Error happen when crawling %s' % request.url)
                self.logger.error(e)
                request.retry_times -= 1
                self.logger.debug('Retrying %s' % request.url)
        else:
            self.logger.debug('Gave up retry %s, total retry %d times' % (request.url, request.retry_times + 1))
            response = requests.Response()
            response.status_code, response.url = 404, request.url

        self.logger.debug('[%d] Scraped from %s' % (response.status_code, response.url))
        # set meta
        response.meta = request.meta
        try:
            results = request.callback(response)
        except Exception as e:
            self.logger.error(e)
            return
        if not results:
            return
            # if Request is results, keep request
        proxy_results = list()
        for x in results:
            if isinstance(x, async_request.Request):
                self.requests.append(x)
            else:
                proxy_results.append(x)
        if self.result_callback and proxy_results:
            self.result_callback(proxy_results)