import json
from aiohttp import web
from .proxy import Proxy

class ProxyWebApi(Proxy):
    '''路由接口'''
    async def get(self, request):
        data = await request.post()
        proxy = self.sql.pop() if not data else self.sql.get(iptype=data.get('type'))
        return web.Response(text=proxy.json())

    async def welcome(self, request):
        text = 'Welcome! go to "./get" to get a proxy, post usage: {"type": "http/s"}'
        return web.Response(text=text)

    def run(self):
        app = web.Application()
        app.add_routes([web.get('/', self.welcome),
                        web.get('/get', self.get),
                        web.post('/get', self.get)])
        web.run_app(app)

def web_app():
    w = ProxyWebApi()
    w.run()