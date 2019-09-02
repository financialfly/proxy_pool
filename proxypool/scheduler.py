import time
from multiprocessing import Process

from proxypool.crawler import RequestPoxy
from proxypool.settings import LOWER_LIMIT, UPPER_LIMIT, INTERVAL_TIME
from proxypool.web import ProxyWebApp


def request_proxy():
    r = RequestPoxy()
    while True:
        r.start_request()
        time.sleep(INTERVAL_TIME)


def run_web():
    w = ProxyWebApp()
    w.run()


def start():
    pros = list()
    funcs = [request_proxy, run_web]
    for f in funcs:
        p = Process(target=f)
        pros.append(p)
        p.start()

    for p in pros:
        p.join()


if __name__ == '__main__':
    start()