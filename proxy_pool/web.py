import json
from aiohttp import web
from .proxy import Proxy

class ProxyWebApi(Proxy):

    async def handle(self, request):
        proxy = {'proxy': self.sql.get()}
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

def web_app():
    w = ProxyWebApi()
    w.run()