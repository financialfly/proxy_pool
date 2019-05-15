import time
from .getter import ProxyGetter
from .checker import ProxyChecker
from .settings import LOWER_LIMIT, UPPER_LIMIT, INTERVAL_TIME
from .utils import get_logger
from .web import ProxyWebApp
from multiprocessing import Process

class Scheduler(object):

    def __init__(self):
        self.logger = get_logger('Scheduler')

    def get(self):
        getter = ProxyGetter()
        current_checked_proxies = getter.sql.length
        current_uncheck_proxies = getter.sql.raw_length
        while True:
            self.logger.info("Current valid proxies's count is {}".format(current_checked_proxies))
            if current_checked_proxies < UPPER_LIMIT:
                if current_uncheck_proxies > UPPER_LIMIT:
                    self.logger.info('Too many proxies waiting for check, will wait for checked')
                    time.sleep(INTERVAL_TIME)
                else:
                    getter.get()
            else:
                time.sleep(INTERVAL_TIME)
            current_checked_proxies = getter.sql.length
            current_uncheck_proxies = getter.sql.raw_length

    def check(self):
        checker = ProxyChecker()
        current_raw_proxies = checker.sql.raw_length
        while True:
            self.logger.info("Current raw proxies's count is {}".format(current_raw_proxies))
            if current_raw_proxies != 0:
                checker.check()
            else:
                time.sleep(INTERVAL_TIME)
            current_raw_proxies = checker.sql.raw_length

    def run_web(self):
        web = ProxyWebApp()
        web.run()

    def start(self):
        pros = list()
        funcs = [self.get, self.check, self.run_web]
        for f in funcs:
            p = Process(target=f)
            pros.append(p)
            p.start()

        for p in pros:
            p.join()