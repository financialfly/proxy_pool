from proxypool.db.sqlite import ProxySql
from proxypool.proxy import formproxy

if __name__ == '__main__':
    s = ProxySql()
    s.put(formproxy('http', '12347.122.45'))
    print(s.get_raw())