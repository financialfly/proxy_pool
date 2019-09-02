from aiohttp import web
from proxypool.db import DbClient


class ProxyWebApp(object):
    '''网络接口'''

    def __init__(self):
        self._db = None

    def __del__(self):
        if self._db is not None:
            self._db.close()

    @property
    def db(self):
        if self._db is None:
            self._db = DbClient()
        return self._db

    async def get(self, request):
        data = await request.post()
        proxy = self.db.pop() if not data else self.db.pop(iptype=data.get('type'))
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