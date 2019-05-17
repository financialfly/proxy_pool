import time
from .get import ProxyGetter
from .check import ProxyChecker
from .settings import LOWER_LIMIT, UPPER_LIMIT, INTERVAL_TIME
from .logs import get_logger
from .web import ProxyWebApp
from multiprocessing import Process

class Scheduler(object):

    def __init__(self):
        self.logger = get_logger('Scheduler')

    def get(self):
        getter = ProxyGetter()
        while True:
            uncheck_count, checked_count = getter.db.count()
            self.logger.info("Current valid proxies's count is {}".format(checked_count))
            if checked_count < UPPER_LIMIT:
                if uncheck_count > LOWER_LIMIT:
                    self.logger.info('Too many proxies waiting for check, will wait for checked')
                    time.sleep(INTERVAL_TIME)
                else:
                    getter.get()
            else:
                time.sleep(INTERVAL_TIME)

    def check(self):
        checker = ProxyChecker()
        while True:
            uncheck_count = checker.db.count(query_checked=False)
            self.logger.info("Current raw proxies's count is {}".format(uncheck_count))
            if uncheck_count != 0:
                checker.check()
            else:
                time.sleep(INTERVAL_TIME)

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