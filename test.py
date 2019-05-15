from proxypool.db import DbClient
from proxypool.proxy import formproxy

if __name__ == '__main__':
    s = DbClient()
    s.put(formproxy('http', '12347.122.45'))
    print(s.get_raw())