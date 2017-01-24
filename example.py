"""
This is a long description of the service.

To configure it, you may specify config
parameters on command-line or env variables.
Some parameters can contain secrets. Their
value may be specified as "secret:foo",
in which case, it will be read from
/run/secrets/foo file.
"""
import argparse
import logging
import time

from prometheus_client import Summary

from em_tools import setup_config, setup_logging, setup_metrics
from em_tools.metrics import setup_metrics, registry

config_vars = {
    'DB_USER':      dict(default='example', help='database user (default "%(default)s")'),
    'DB_PASSWORD':  dict(default='example', secret=True, help='(secret) database password'),
    'DB_HOSTNAME':  dict(required=True, help='database hostname'),
    'DB_PORT':      dict(default='5432', help='database port (default "%(default)s")'),
}

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request', registry=registry)

@REQUEST_TIME.time()
def sample_request_handler():
    time.sleep(.01)

def main():
    parser = argparse.ArgumentParser(
        usage='example.py [<option>..]',
        description=__doc__)
    setup_config(parser, config_vars)
    config = parser.parse_args()
    setup_logging(config)
    setup_metrics(config)

    logging.info('Starting %s', config.SERVICE_NAME)
    logging.warning('sample warning')
    logging.error('sample error')

    if config.METRICS:
        logging.info('Running simulated traffic for 30s')
        for _ in range(3000):
            sample_request_handler()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
