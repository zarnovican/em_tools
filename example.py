"""
This is a long description of the service.

To configure it, you may specify config
parameters on command-line or env variables.
Some parameters can contain secrets. Their
value may be specified as "secret:foo",
in which case, it will be read from
/run/secrets/foo file.
"""
import logging
import time

from prometheus_client import Summary

from em_tools import basic_setup
from em_tools.metrics import registry

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
    config = basic_setup(service_name='example.py', description=__doc__, config_vars=config_vars)

    print(config)
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
