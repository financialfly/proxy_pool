"""
error
"""

class ProxyPoolEmpty(BaseException):

    def __str__(self):
        return 'Proxy pool is empty'