'''
代理池
'''

__author__ = 'financial'

def run():
    from .scheduler import Scheduler
    s = Scheduler()
    s.start()