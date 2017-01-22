
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
    url = '{}:9091'.format(config.METRICS_HOST)
    interval = config.METRICS_INTERVAL
    job = config.SERVICE_NAME
    logging.info('Prometheus metrics push thread started: url=%s, interval=%ds', url, interval)
    while True:
        time.sleep(interval)
        try:
            push_to_gateway(url, job=job, registry=registry)
        except URLError as e:
            logging.warning('Prometheus push failed "http://%s/" %s', url, str(e))


def setup_prometheus(config):
    """start Prometheus pushing thread"""

    if not config.METRICS:
        logging.info('Prometheus metrics pushing is disabled, which is ok.')
        return None

    thread = threading.Thread(name='prometheus_pusher', target=prometheus_pusher, args=(config, ))
    thread.daemon = True
    thread.start()
    return thread
