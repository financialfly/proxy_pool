import logging

import pymysql
from pymysql.cursors import Cursor
from pymysql.err import IntegrityError

from proxypool.settings import HOST, PORT, PASSWORD, USER, DATABASE

try:
    from proxypool.settings import TABLE
except:
    TABLE = None

from proxypool.proxy import formproxy
from proxypool.db.err import ProxyPoolEmpty


class MySqlClient(object):
    '''
    状态值
    0未验证，1通过验证未使用，2已使用
    '''
    def __init__(self):
        self.db_params = dict(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        self.logger = logging.getLogger('ProxyPool-MysqlClient')
        self.conn = self.init_conn()
        if not TABLE:
            self.create_table()
        else:
            self.table = TABLE

    def init_conn(self):
        """
        :return: mysql connection
        """
        return pymysql.connect(**self.db_params)

    def create_table(self):
        self.table = 'proxypool'
        query = f'''
            CREATE TABLE IF NOT EXISTS {self.table}(
            proxy VARCHAR(50) PRIMARY KEY, 
            status TINYINT NOT NULL DEFAULT 0 COMMENT '0未验证，1通过验证，2未通过验证，3已使用', 
            type VARCHAR(20) COMMENT 'http/https',
            INDEX proxy_index (proxy))'''
        self.exec(query)

    def close(self):
        self.conn.close()

    def exec(self, query, cursor=Cursor, commit=True):
        '''执行sql语句'''
        with self.conn.cursor(cursor) as c:
            c.execute(query)
            if not commit:
                return c
        self.conn.commit()

    def runquery(self, query, cursor=Cursor):
        with self.conn.cursor(cursor) as c:
            c.execute(query)
            return c.fetchall()

    def get(self, status=1, iptype=None):
        '''获取代理'''
        query = f'SELECT type, proxy FROM {self.table} WHERE status={status}'
        if iptype:
            query += f' AND type="{iptype}"'
        query += ' LIMIT 1'
        proxy = self.runquery(query)
        if proxy:
            t, addr = proxy[0]
            return formproxy(t, addr)

    def pop(self, iptype=None):
        '''获取一条代理，并从数据库删除'''
        proxy = self.get(iptype=iptype)
        if not proxy:
            raise ProxyPoolEmpty()
        self.delete(proxy)
        return proxy

    def put(self, proxy):
        '''把代理放进数据库'''
        query = f'INSERT INTO {self.table} (type, proxy, status) VALUES("{proxy.type}", "{proxy.addr}", "{proxy.status}")'
        try:
            self.exec(query)
        except IntegrityError:
            self.logger.debug('Proxy already exist')

    def update(self, proxy, status):
        '''更新'''
        query = 'UPDATE %s SET status=%d WHERE proxy="%s"' % (self.table, status, proxy.addr)
        self.exec(query)

    def delete(self, proxy):
        '''删除'''
        query = 'DELETE FROM %s WHERE proxy="%s"' % (self.table, proxy.addr)
        self.exec(query)
        self.logger.debug('Deleted proxy %s' % proxy)

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

    def __len__(self):
        conn = self.init_conn()
        try:
            with conn.cursor() as cur:
                query = f'SELECT COUNT(proxy) FROM {self.table} WHERE status={1}'
                cur.execute(query)
                return cur.fetchone()[0]
        finally:
            conn.close()
