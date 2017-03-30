
import logging
import threading
import time

try:
    # Py3
    from urllib.error import URLError
except ImportError:
    # Py2
    from urllib2 import URLError

from prometheus_client import CollectorRegistry, push_to_gateway


registry = CollectorRegistry()


def prometheus_pusher(config):
    url = '{}:9091'.format(config.PROMETHEUS_HOST)
    interval = config.PROMETHEUS_PUSH_INTERVAL
    job = config.SERVICE_NAME
    grouping_key = { 'slot': config.TASK_SLOT, }
    logging.info('Prometheus metrics push thread started: url=%s, interval=%ds', url, interval)
    while True:
        time.sleep(interval)
        try:
            push_to_gateway(url, job=job, registry=registry, grouping_key=grouping_key)
        except URLError as e:
            logging.warning('Prometheus push failed "http://%s/" %s', url, str(e))


def setup_metrics(config):
    """start Prometheus pushing thread"""

    if not config.PROMETHEUS_HOST:
        logging.info('Prometheus metrics pushing is disabled, which is ok.')
        return None

    thread = threading.Thread(name='prometheus_pusher', target=prometheus_pusher, args=(config, ))
    thread.daemon = True
    thread.start()
    return thread
