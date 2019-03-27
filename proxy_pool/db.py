import json
import pymysql
from pymysql.cursors import Cursor
from pymysql.err import IntegrityError

from .utils import get_logger
from .settings import HOST, PORT, PASSWORD, USER, DATABASE, TABLE

class _Proxy(object):
    '''代理'''
    __slots__ = ['type', 'addr']

    def __init__(self, iptype, ipaddr):
        super().__init__()
        self.type = iptype.lower()
        self.addr = ipaddr.strip()

    def __repr__(self):
        return '%s' % {self.type: self.addr}

    def json(self):
        return json.dumps({self.type: self.addr})

    def dict(self):
        return {self.type: self.addr}

def formproxy(iptype, ipaddr):
    return _Proxy(iptype, ipaddr)

class ProxySql(object):
    '''
    状态值
    0未验证，1通过验证未使用，2已使用
    proxy[0],proxy[1] 对应 type, addr， 如http,127.0.0.1:2555
    '''
    def __init__(self):
        self.conn = pymysql.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        self.logger = get_logger('sql')
        self.table = TABLE

    def _exec(self, query, cursor=Cursor, commit=False):
        '''执行sql语句'''
        with self.conn.cursor(cursor) as c:
            c.execute(query)
            if not commit:
                return c
        self.conn.commit()

    def get(self, iptype=None):
        '''获取一条代理数据'''
        proxy = self._get(status=1, iptype=iptype)[0]
        return formproxy(proxy[0], proxy[1])

    def get_raw(self, count=1):
        '''获取没有经过验证的代理'''
        proxies = self._get(status=0, count=count)
        proxies = [formproxy(p[0], p[1]) for p in proxies]
        return proxies[0] if count == 1 else proxies

    def pop(self, iptype=None):
        '''获取一条代理，并从数据库删除'''
        proxy = self._get(status=1, iptype=iptype)[0]
        proxy = formproxy(proxy[0], proxy[1])
        self.delete(proxy)
        return proxy

    def update_useful(self, proxy):
        '''更新经过验证的代理状态'''
        return self.update(proxy, status=1)

    def put(self, proxy):
        '''把代理放进数据库'''
        query = 'INSERT INTO %s (type, proxy) VALUES("%s", "%s")' % (self.table, proxy.type, proxy.addr)
        try:
            self._exec(query, commit=True)
        except IntegrityError:
            self.logger.debug('proxy already exist')

    def put_many(self, proxies):
        '''把一些代理放进代理池'''
        query = 'INSERT IGNORE INTO %s (type, proxy) VALUES' % self.table
        for proxy in proxies:
            value = '("%s", "%s"), ' % (proxy.type, proxy.addr)
            query += value
        # 有的时候代理为空，会报错
        try:
            self._exec(query[:-2], commit=True)
        except:
            pass

    def _get(self, status, count=1, iptype=None):
        '''获取代理'''
        query = 'SELECT type, proxy FROM %s WHERE status=%d LIMIT 0,%d' % (self.table, status, count)
        if iptype:
            query = 'SELECT type, proxy FROM %s WHERE status=%d AND type="%s" LIMIT 0,%d' %(self.table, status, iptype, count)
        c = self._exec(query)
        if c.rowcount > 0:
            return c.fetchall()
        else:
            return 'Get proxy FAILED because proxy pool is empty.'

    @property
    def length(self):
        '''有用代理的数量'''
        return self._length(status=1)

    @property
    def raw_length(self):
        '''未经验证的代理数量'''
        return self._length(status=0)

    def _length(self, status):
        query = 'SELECT COUNT(proxy) FROM %s WHERE status=%d' % (self.table, status)
        c = self._exec(query)
        return c.fetchone()[0]

    def update(self, proxy, status):
        '''更新'''
        query = 'UPDATE %s SET status=%d WHERE proxy="%s" LIMIT 1' % (self.table, status, proxy.addr)
        self._exec(query, commit=True)

    def delete(self, proxy):
        '''删除'''
        query = 'DELETE FROM %s WHERE proxy="%s" LIMIT 1' % (self.table, proxy.addr)
        self._exec(query, commit=True)
        self.logger.info('deleted proxy %s' % proxy)

    def clean(self, status):
        '''清除某个状态的代理'''
        query = 'DELETE FROM %s WHERE status=%d' % (self.table, status)
        self._exec(query, commit=True)
        self.logger.info('proxies that status is %d were cleared.' % status)

    def clean_all(self):
        '''清空代理池'''
        query = 'TRUNCATE TABLE %s' % self.table
        self._exec(query, commit=True)
        self.logger.info('all proxies were deleted.')