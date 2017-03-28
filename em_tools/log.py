"""
Setup basic logging
"""
import logging
import logging.handlers
import os

from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging as setup_sentry

log_level_map = {
    'error':    logging.ERROR,
    'warning':  logging.WARNING,
    'info':     logging.INFO,
    'debug':    logging.DEBUG,
}


def setup_logging(config, version=None):
    """setup logging formatter/handlers

    'config' is the ouput of argparse 'parse_args()'"""

    if config.LOG_TARGET == 'syslog':
        if not os.path.exists('/dev/log'):
            print('Unable to find /dev/log. Is syslog present ?')
            open('/dev/log')                # raise IOError
        syslog_id = '{}[{}]'.format(config.SERVICE_NAME, config.TASK_SLOT)
        print('Logging is redirected to systemd journal. Tail with "journalctl -t {} -f"'.format(config.SERVICE_NAME))
        handler = logging.handlers.SysLogHandler(address='/dev/log')
        formatter = logging.Formatter('{}: %(name)s %(message)s'.format(syslog_id))
    else:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)

    if config.SENTRY_DSN:
        sentry_args = {}
        sentry_args['level'] = logging.WARNING
        sentry_args['tags'] = { 'service': config.SERVICE_NAME, 'slot': config.TASK_SLOT, }
        if version is not None:
            sentry_args['release'] = version
        setup_sentry(SentryHandler(config.SENTRY_DSN, **sentry_args))

    logger.setLevel(log_level_map.get(config.LOG_LEVEL, logging.INFO))
