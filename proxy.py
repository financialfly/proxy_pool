import time
from getter import crawl_funcs
from checker import check_proxy
from db import CheckedProxyRedis, RawCheckedProxyRedis
from settings import LOWER_LIMIT, UPPER_LIMIT
from _proxy import ProxyCrawler

_redis = CheckedProxyRedis()
_Rredis = RawCheckedProxyRedis()

def get(interval=3):
    while True:
        if _redis.length > UPPER_LIMIT:
            pass
        elif _redis.length < LOWER_LIMIT:
            for func in crawl_funcs():
                crawler = ProxyCrawler(func, _Rredis)
                crawler.run()
        time.sleep(interval)

def check():
    while True:
        if not _Rredis.length == 0:
            proxy = _Rredis.pop()
            proxy = check_proxy(proxy)
            if proxy:
                _redis.put(proxy)