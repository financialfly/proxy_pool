'''
两个类，一个用来存储经过验证的代理，一个用来存储没有验证的代理
'''
import redis
from settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWD

class ProxyRedis(object):

    key = None

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWD, *args, **kwargs):
        self._db = redis.Redis(host=host, port=port, password=password, *args, **kwargs)

    def get(self, count=1):
        """
        get proxies from redis
        """
        proxies = self._db.lrange(self.key, 0, count - 1)
        self._db.ltrim(self.key, count, -1)
        return proxies

    def put(self, proxy):
        """
        add proxy to right top
        """
        self._db.rpush(self.key, proxy)

    def pop(self):
        """
        get proxy from right.
        """
        return self._db.rpop(self.key).decode('utf-8')

    @property
    def length(self):
        """
        get length from queue.
        """
        return self._db.llen(self.key)

    def flush(self):
        """
        flush db
        """
        self._db.flushall()

class CheckedProxyRedis(ProxyRedis):
    key = 'proxies'

class RawCheckedProxyRedis(ProxyRedis):
    key = 'unchecked_proxies'