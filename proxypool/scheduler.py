import time
from multiprocessing import Process

from proxypool.crawler import ProxyCrawler
from proxypool.settings import CHECKED_INTERVAL
from proxypool.web import ProxyWebApp


def request_proxy():
    r = ProxyCrawler()
    while True:
        r.start_request()
        time.sleep(CHECKED_INTERVAL)


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