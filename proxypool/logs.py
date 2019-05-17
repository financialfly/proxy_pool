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

    extra = {'appname':'ProxyPool.%s' % appname}

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