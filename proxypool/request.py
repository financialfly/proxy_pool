'''
基于asyncio和requests做的异步下载器
'''
import asyncio
import random
import requests
# import types
from functools import partial
from proxypool.logger import get_logger

class Request(object):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    ]

    def __init__(self, url, headers=None, retry_times=3,
                 timeout=5, callback=None, meta=None,
                 cookies=None, proxies=None):
        self.url = url
        self._headers = headers
        self.retry_times = retry_times
        self.timeout = timeout
        self.callback = callback
        self.meta = meta or dict()
        self.cookies = cookies
        self.proxies = proxies

    @property
    def headers(self):
        if self._headers is None:
            return {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en',
                'User-Agent': random.choice(self.user_agents)
            }
        return self._headers

class Crawler(object):

    def __init__(self, requests, result_callback=None, logger=None):
        '''
        初始化crawler
        :param requests: Request请求列表
        :param result_callback: 请求结束后的结果处理回调函数
        :param logger: logger
        '''
        self.requests = requests
        self.loop = asyncio.get_event_loop()
        self.result_callback = result_callback
        self.logger = logger if logger else get_logger('Crawler')

    async def get_html(self, request):
        self.logger.debug('Crawling {}'.format(request.url))
        future = self.loop.run_in_executor(None,
                                           partial(requests.get,
                                                   request.url,
                                                   headers=request.headers,
                                                   timeout=request.timeout,
                                                   cookies=request.cookies,
                                                   proxies=request.proxies
                                                   ))
        while request.retry_times >= 0:
            try:
                r = await future
                r.meta = request.meta
                break
            except Exception as e:
                # self.logger.info('Error happen when crawling %s' % request.url)
                # self.logger.error(e)
                request.retry_times -= 1
                # self.logger.info('Retrying %s' % request.url)
        else:
            # self.logger.info('Gave up retry %s, total retry %d times' % (request.url, request.retry_times + 1))
            r = requests.Response()
            r.meta = request.meta
            r.status_code, r.url = 404, request.url

        self.logger.debug('[%d] Scraped from %s' % (r.status_code, r.url))
        results = request.callback(r)
        if not results:
            return
        proxy_results = list()
        for x in results:
            if isinstance(x, Request):
                self.requests.append(x)
            else:
                proxy_results.append(x)
                # if self.result_callback:
                #     self.result_callback(result)
        if self.result_callback and proxy_results:
            self.result_callback(proxy_results)

    def run(self):
        while self.requests:
            tasks = [self.get_html(req) for req in self.requests]
            self.requests = list()
            self.loop.run_until_complete(asyncio.gather(*tasks))

    def stop(self):
        self.loop.close()
        self.logger.debug('crawler stopped')