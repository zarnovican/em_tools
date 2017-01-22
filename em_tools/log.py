"""
Setup basic logging
"""
import logging
import logging.handlers
import os

from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging as setup_sentry

verbosity_map = {
    0:  logging.ERROR,
    1:  logging.WARNING,
    2:  logging.INFO,
    3:  logging.DEBUG,
}


def setup_logging(config):
    """setup logging formatter/handlers

    'config' is the ouput of argparse 'parse_args()'"""

    syslog_present = os.path.exists('/dev/log')
    if syslog_present and config.LOG_TARGET == 'syslog':
        syslog_id = config.SERVICE_NAME
        if config.DOCKER_TASK_SLOT:
            syslog_id = '{}[{}]'.format(config.SERVICE_NAME, config.DOCKER_TASK_SLOT)
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
        handler = SentryHandler(config.SENTRY_DSN, level=logging.WARNING)
        setup_sentry(handler)

    logger.setLevel(verbosity_map.get(config.VERBOSITY, logging.INFO))

    if config.LOG_TARGET == 'syslog' and not syslog_present:
        logging.warning('Requested syslog logging, but syslog was not found, using console instead.')
