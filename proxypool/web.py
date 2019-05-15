from aiohttp import web
from .db import DbClient

class ProxyWebApp(object):
    '''网络接口'''

    async def get(self, request):
        data = await request.post()
        # todo 待改进
        db = DbClient()
        proxy = db.pop() if not data else db.pop(iptype=data.get('type'))
        db.close()
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