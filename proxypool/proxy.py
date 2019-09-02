import json


class Proxy(object):
    '''代理'''
    __slots__ = ['type', 'addr', 'status']

    def __init__(self, iptype, ipaddr):
        self.type = iptype.lower()
        self.addr = ipaddr.strip()
        self.status = 0

    def json(self):
        return json.dumps({self.type: self.addr})

    def dict(self):
        return {self.type: self.addr}

    def __str__(self):
        return  '%s://%s' % (self.type, self.addr)

    __repr__ = __str__


def formproxy(iptype, ipaddr):
    return Proxy(iptype, ipaddr)