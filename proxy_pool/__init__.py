from .scheduler import ProxyScheduler
from .web import ProxyWebApi

def get(interval=5):
    s = ProxyScheduler()
    return s.get_proxy(interval)

def check(interval=5):
    s = ProxyScheduler()
    return s.check_proxy(interval)

def run_web():
    a = ProxyWebApi()
    return a.run()