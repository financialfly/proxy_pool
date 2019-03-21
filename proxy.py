import time
from getter import crawl_funcs
from checker import ProxyChecker
from db import ProxySql
from settings import LOWER_LIMIT, UPPER_LIMIT
from _proxy import ProxyCrawler

sql =ProxySql()

def get(interval=3):
    while True:
        print(sql.length)
        if sql.length > UPPER_LIMIT:
            pass
        elif sql.length < LOWER_LIMIT:
            if sql.raw_length > 500:
                pass
            else:
                for func in crawl_funcs():
                    crawler = ProxyCrawler(func, sql)
                    crawler.run()
        else:
            pass
        time.sleep(interval)

def check():
    checker = ProxyChecker(db=sql)
    print(sql.length)
    while True:
        if sql.raw_length != 0:
            count = 10 if sql.raw_length > 10 else sql.raw_length
            if count == 1:
                proxy = sql.get_raw()
                checker.check_one(proxy)
            else:
                checker.check_many(count=count)
        else:
            pass