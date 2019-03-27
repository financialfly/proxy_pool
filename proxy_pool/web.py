import json
from aiohttp import web
from .proxy import Proxy

class ProxyWebApi(Proxy):
    '''路由接口'''
    async def get_proxy(self, request):
        proxy = self.sql.pop()
        return web.Response(text=proxy.json())

    async def welcome(self, request):
        text = 'Welcome! go to "./get" to get a proxy'
        return web.Response(text=text)

    def run(self):
        app = web.Application()
        app.add_routes([web.get('/', self.welcome),
                        web.get('/get', self.get_proxy)])
        web.run_app(app)

def web_app():
    w = ProxyWebApi()
    w.run()