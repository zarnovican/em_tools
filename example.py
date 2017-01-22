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

from em_tools.config import add_config_vars
from em_tools.log import setup_logging

config_vars = {
    'DB_USER':      dict(default='example', help='database user (default "%(default)s")'),
    'DB_PASSWORD':  dict(default='example', secret=True, help='(secret) database password'),
    'DB_HOSTNAME':  dict(required=True, help='database hostname'),
    'DB_PORT':      dict(default='5432', help='database port (default "%(default)s")'),
}


def main():
    parser = argparse.ArgumentParser(
        usage='example.py [<option>..]',
        description=__doc__)
    add_config_vars(parser, config_vars)
    config = parser.parse_args()
    setup_logging(config)

    logging.info('Starting %s', config.SERVICE_NAME)
    logging.warning('sample warning')
    logging.error('sample error')


if __name__ == '__main__':
    main()
