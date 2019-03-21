import requests
import random
import time

from requests.models import Response

class WebRequest(object):

    @property
    def logger(self):
        return get_logger('request')

    @property
    def user_agent(self):
        """
        return an User-Agent at random
        :return:
        """
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        ]
        return random.choice(ua_list)

    @property
    def header(self):
        """
        basic header
        :return:
        """
        return {'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Accept-Language': 'zh-CN,zh;q=0.8'}

    def get(self, url, header=None, retry_time=5, timeout=30,
            retry_flag=[], retry_interval=5, *args, **kwargs):
        """
        get method
        :param url: target url
        :param header: headers
        :param retry_time: retry time when network error
        :param timeout: network timeout
        :param retry_flag: if retry_flag in content. do retry
        :param retry_interval: retry interval(second)
        :param args:
        :param kwargs:
        :return:
        """
        self.logger.debug('crawling %s' % url)
        headers = self.header
        if header and isinstance(header, dict):
            headers.update(header)
        while True:
            try:
                html = requests.get(url, headers=headers, timeout=timeout, **kwargs)
                if any(f in html.content for f in retry_flag):
                    raise Exception
                return html
            except Exception as e:
                self.logger.debug('Request error cause by: %s' % e)
                retry_time -= 1
                if retry_time <= 0:
                    # 多次请求失败
                    resp = Response()
                    resp.status_code = 400
                    return resp
                time.sleep(retry_interval)

def get_html(url, *args, **kwargs):
    w = WebRequest()
    return w.get(url, *args, **kwargs)


import logging

handlers = dict()

def get_logger(appname, level='INFO'):
    '''
    获取logger, 如果传入了dirname，则会将log写入到文件中
    :param appname: 自定义名称，用于区别
    :param dirname: log文件夹下的自定义文件夹名称
    '''
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    _level = levels.get(level)
    if not _level:
        raise ValueError('param level must be one of the levels list {}'.format([k for k in levels.keys()]))

    extra = {'appname':'proxy.%s' % appname}

    logger = logging.getLogger(__name__)

    global handlers
    syslog = handlers.get('syslog')
    if not syslog:
        syslog = logging.StreamHandler()
        handlers['syslog'] = syslog

    formatter = logging.Formatter(
        fmt='%(asctime)s [%(appname)s] %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)
    logger.setLevel(_level)
    logger = logging.LoggerAdapter(logger, extra)
    return logger