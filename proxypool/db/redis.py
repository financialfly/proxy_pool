import redis
from proxypool.proxy import Proxy


class RedisClient:
    """使用集合
    列表不支持去重
    有序集合pop操作windows不支持"""
    conn_pool = None

    def __init__(self):
        if self.conn_pool is None:
            self.conn_pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.db = redis.Redis(connection_pool=self.conn_pool)
        self.keys = {'http': 'http_proxy', 'https': 'https_proxy'}

    def delete(self, proxy):
        key = self.keys[proxy.type]
        self.db.srem(key, proxy.str())

    def pop(self, iptype='http'):
        key = self.keys[iptype]
        return self.db.spop(key)

    def update_useful(self, proxy):
        key = self.keys[proxy.type]
        self.db.sadd(key, proxy.str())

    def put(self, proxy):
        key = self.keys[proxy.type]
        self.db.sadd(key, proxy.str())

    def get(self, count=1, iptype=None) -> list:
        proxy_list = []
        if iptype is not None:
            keys = [self.keys[iptype]]
        else:
            keys = self.keys.values()
        for k in keys:
            _, proxies = self.db.sscan(k, count=count)
            proxy_list.extend(Proxy.fromstr(p) for p in proxies)
            length = len(proxy_list)
            if length < count:
                count -= length
            else:
                return proxy_list
        return proxy_list

    def __len__(self):
        l = 0
        for v in self.keys.values():
            l += self.db.scard(v)
        return l
