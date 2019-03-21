import pymysql
from pymysql.cursors import Cursor
from pymysql.err import IntegrityError
from utils import get_logger

class ProxySql(object):
    '''
    状态值
    0未验证，1通过验证未使用，2已使用
    '''
    def __init__(self):
        self.conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='1234',
            database='lzz'
        )
        self.logger = get_logger('sql')

    def _exec(self, query, cursor=Cursor, commit=False):
        with self.conn.cursor(cursor) as c:
            c.execute(query)
            if not commit:
                return c
        self.conn.commit()

    def get(self):
        return self._get(status=1)

    def get_raw(self, count=1):
        proxies = self._get(status=0, count=count)
        if count != 1:
            proxies = [p[0] for p in proxies]
        return proxies

    def pop(self):
        return self._get(status=1, delete=True)

    def update_useful(self, proxy):
        return self.update(proxy, status=1)

    def put(self, proxy, status=0):
        query = 'INSERT INTO proxies (proxy, status) VALUES("%s", %d)' % (proxy, status)
        try:
            self._exec(query, commit=True)
        except IntegrityError:
            self.logger.debug('proxy already exist')

    def _get(self, status, delete=False, count=1):
        query = 'SELECT proxy FROM proxies WHERE status=%d LIMIT 0,%d' % (status, count)
        c = self._exec(query)
        if c.rowcount > 0:
            if count != 1:
                return c.fetchall()
            proxy = c.fetchone()[0]
            if status == 1:
                self.update(proxy, status=2)
            if delete:
                self.delete(proxy)
            return proxy
        else:
            return 'Get proxy FAILED because proxy pool is empty.'

    @property
    def length(self):
        return self._length(status=1)

    @property
    def raw_length(self):
        return self._length(status=0)

    def _length(self, status):
        query = 'SELECT COUNT(proxy) FROM proxies WHERE status=%d' % status
        c = self._exec(query)
        return c.fetchone()[0]

    def update(self, proxy, status):
        query = 'UPDATE proxies SET status=%d WHERE proxy="%s" LIMIT 1' % (status, proxy)
        self._exec(query, commit=True)

    def delete(self, proxy):
        query = 'DELETE FROM proxies WHERE proxy="%s" LIMIT 1' % proxy
        self._exec(query, commit=True)
        self.logger.debug('deleted proxy %s' % proxy)

    def clean(self, status):
        query = 'DELETE FROM proxies WHERE status=%d' % status
        self._exec(query, commit=True)

    def clean_all(self):
        query = 'TRUNCATE TABLE proxies'
        self._exec(query, commit=True)
        self.logger.debug('all proxies were deleted.')