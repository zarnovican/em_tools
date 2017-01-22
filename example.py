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

from em_tools.config import add_config_vars

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
    args = parser.parse_args()

    print('Config parameters have the following values:')
    print(args)


if __name__ == '__main__':
    main()
