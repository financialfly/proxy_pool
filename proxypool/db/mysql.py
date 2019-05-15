import pymysql
from pymysql.cursors import Cursor
from pymysql.err import IntegrityError

from proxypool.proxy import formproxy
from proxypool.utils import get_logger
from proxypool.settings import HOST, PORT, PASSWORD, USER, DATABASE

try:
    from proxypool.settings import TABLE
except NameError:
    TABLE = None

class MySqlClient(object):
    '''
    状态值
    0未验证，1通过验证未使用，2已使用
    proxy[0],proxy[1] 对应 type, addr， 如http,127.0.0.1:2555
    '''
    def __init__(self):
        self.db_params = dict(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        self.conn = self.get_conn()
        self.logger = get_logger('db')
        self.table = TABLE
        if not self.table:
            self.create_table()

    def create_table(self):
        query = '''
                CREATE TABLE proxies(
                    proxy VARCHAR(50) PRIMARY KEY,
                    status TINYINT NOT NULL COMMENT '0未验证，1通过验证，2未通过验证，3已使用'
                    type VARCHAR(20) COMMENT 'http/https',
                    INDEX proxy_index (proxy)
                    )
                '''
        self.exec(query)
        self.table = 'proxies'

    def get_conn(self, **kwargs):
        print('Getting connection from MySql...')
        retry_times = 3
        while retry_times > 0:
            try:
                return pymysql.connect(**self.db_params, **kwargs)
            except pymysql.err.OperationalError as e:
                print(e)
                retry_times -= 1

    def close(self):
        self.conn.close()

    def exec(self, query, cursor=Cursor, commit=True):
        '''执行sql语句'''
        with self.conn.cursor(cursor) as c:
            c.execute(query)
            if not commit:
                return c
        self.conn.commit()

    def runQuery(self, query, cursor=Cursor):
        with self.conn.cursor(cursor) as c:
            c.execute(query)
            return c.fetchall()

    def get(self, iptype=None):
        '''获取一条代理数据'''
        proxy = self._get(status=1, iptype=iptype)[0]
        return formproxy(proxy[0], proxy[1])

    def get_raw(self, count=1, iptype=None):
        '''获取没有经过验证的代理'''
        proxies = self._get(status=0, count=count, iptype=iptype)
        if proxies:
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
            self.exec(query)
        except IntegrityError:
            self.logger.debug('Proxy already exist')

    def put_many(self, proxies):
        '''把一些代理放进代理池'''
        query = 'INSERT IGNORE INTO %s (type, proxy) VALUES' % self.table
        for proxy in proxies:
            value = '("%s", "%s"), ' % (proxy.type, proxy.addr)
            query += value
        # 有的时候代理为空，会报错
        try:
            self.exec(query[:-2])
        except:
            pass

    def _get(self, status, count=1, iptype=None):
        '''获取代理'''
        query = 'SELECT type, proxy FROM %s WHERE status=%d LIMIT %d' % (self.table, status, count)
        if iptype:
            query = 'SELECT type, proxy FROM %s WHERE status=%d AND type="%s" LIMIT %d' %(self.table, status, iptype, count)
        return self.runQuery(query)

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
        result = self.runQuery(query)
        return result[0][0]

    def update(self, proxy, status):
        '''更新'''
        query = 'UPDATE %s SET status=%d WHERE proxy="%s"' % (self.table, status, proxy.addr)
        self.exec(query)

    def delete(self, proxy):
        '''删除'''
        query = 'DELETE FROM %s WHERE proxy="%s"' % (self.table, proxy.addr)
        self.exec(query)
        self.logger.info('Deleted proxy %s' % proxy)

    def clean(self, status):
        '''清除某个状态的代理'''
        query = 'DELETE FROM %s WHERE status=%d' % (self.table, status)
        self.exec(query)
        self.logger.info('Proxies that status is %d were cleared.' % status)

    def clean_all(self):
        '''清空代理池'''
        query = 'TRUNCATE TABLE %s' % self.table
        self.exec(query)
        self.logger.info('All proxies were deleted.')