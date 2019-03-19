import json
from aiohttp import web
from _proxy import Proxy
from db import CheckedProxyRedis

class ProxyOffer(Proxy):

    def __init__(self):
        self.redis = CheckedProxyRedis()

    async def handle(self, request):
        proxy = {'proxy': self.redis.pop()}
        proxy = json.dumps(proxy)
        return web.Response(text=proxy)

    async def welcome(self, request):
        text = 'Welcome to Proxies Pool !'
        return web.Response(text=text)

    def run(self):
        app = web.Application()
        app.add_routes([web.get('/', self.welcome),
                        web.get('/get', self.handle)])

        web.run_app(app)

def run_web():
    o = ProxyOffer()
    o.run()