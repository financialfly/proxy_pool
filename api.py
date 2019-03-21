import json
from aiohttp import web
from _proxy import Proxy
from db import ProxySql

class ProxyWebApi(Proxy):

    def __init__(self):
        self.sql = ProxySql()

    async def handle(self, request):
        proxy = {'proxy': self.sql.pop()}
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
    w = ProxyWebApi()
    w.run()