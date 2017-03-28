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
import asyncio
import logging

from prometheus_client import Summary
import prometheus_async

from em_tools import setup_config, setup_logging
from em_tools.metrics import registry
from em_tools.aiometrics import setup_metrics, shutdown_metrics

config_vars = {
    'DB_USER':      dict(default='example', help='database user (default "%(default)s")'),
    'DB_PASSWORD':  dict(default='example', secret=True, help='(secret) database password'),
    'DB_HOSTNAME':  dict(required=True, help='database hostname'),
    'DB_PORT':      dict(default='5432', help='database port (default "%(default)s")'),
}

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request', registry=registry)


@prometheus_async.aio.time(REQUEST_TIME)
async def sample_request_handler():
    await asyncio.sleep(.01)


async def mainloop(config):
    logging.info('Starting %s', config.SERVICE_NAME)
    logging.warning('sample warning')
    logging.error('sample error')

    if config.PROMETHEUS_HOST:
        logging.info('Running simulated traffic for 30s')
        for _ in range(3000):
            await sample_request_handler()


def main():
    parser = argparse.ArgumentParser(usage='aioexample.py [<option>..]', description=__doc__)
    setup_config(parser, config_vars, service_name='aioexample')
    config = parser.parse_args()
    setup_logging(config)
    
    loop = asyncio.get_event_loop()
    pusher_task = setup_metrics(loop, config)
    try:
        loop.run_until_complete(mainloop(config))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception('Main loop finished with: %s', str(e))
    shutdown_metrics(loop, pusher_task)


if __name__ == '__main__':
    main()
