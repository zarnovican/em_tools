"""
Configuration parameters setup

TODO: doc
"""

import argparse
import os
import os.path

from argparse import ArgumentError, _StoreAction


common_config_vars = {
    'SERVICE_NAME': dict(help='service name (default: "%(default)s")'),
    'TASK_SLOT': dict(
        default=1, type=int,
        help='task id within service (default: %(default)s)'),
    'LOG_LEVEL': dict(
        default='info', choices=['error', 'warning', 'info', 'debug'],
        help='logging verbosity: error/warning/info/debug (default: %(default)s)'),
    'SENTRY_DSN': dict(
        secret=True,
        help='(secret) sentry DSN. If set, sentry logger will be configured as well (default: unset)'),
    'LOG_TARGET': dict(
        default='console', choices=['console', 'syslog'],
        help='where to send logs (console/syslog) (default: %(default)s)'),
    'PROMETHEUS_HOST': dict(
        default='',
        help='prometheus pushgateway hostname, non-empty value enables pushing (default: "%(default)s")'),
    'PROMETHEUS_PUSH_INTERVAL': dict(
        default=10, type=int,
        help='how often to push out metrics [s] (default: %(default)ss)'),
}


class StoreSecret(_StoreAction):
    """argparse 'action' to transparently load the secret from file

    if the string value of configuration parameter is "secret:<name>"
    then <name> is considered a filename under /run/secrets/ directory
    For example, input "secret:sentry_dsn" will set the value
    to the content of /run/secrets/sentry_dsn file"""

    def __call__(self, parser, namespace, values, option_string=None):
        if values.startswith('secret:'):
            secret_file = os.path.join('/run/secrets', values[7:])
            try:
                with open(secret_file) as f:
                    values = f.read()
            except IOError as e:
                raise ArgumentError(self, 'Failed to load secret {}'.format(e))

        setattr(namespace, self.dest, values)


def _add_argument(parser, envname, attr):
    """Add argparse long option --ENVNAME

    Option's default is the value of env variable
    (or empty string)."""

    kwargs = attr.copy()

    kwargs.setdefault('type', str)
    kwargs.setdefault('metavar', '<{}>'.format(kwargs['type'].__name__))

    is_secret = kwargs.pop('secret', False)
    if is_secret:
        kwargs['action'] = StoreSecret

    # order of precedence: cli > env > default > ''
    kwargs.setdefault('default', '')
    if os.environ.get(envname, ''):
        kwargs['default'] = os.environ.get(envname, '')

    kwargs.setdefault('required', False)
    if kwargs['required'] and os.environ.get(envname, ''):
        # if env var has a value, then cli option is no longer required
        kwargs['required'] = False

    parser.add_argument('--{}'.format(envname), **kwargs)


def setup_config(parser, config_vars, service_name='dummy', version=None):
    """Add dict of configuration variables to argparse's parser

    It will create two option groups 'mandatory' and 'common'.
    Global config variables are added to common group.
    Service-specific variable are adde to either base or mandatory,
    depending if the variable is required=True."""

    if version is not None:
        parser.add_argument('--version', action='version', version=version)

    mandatory_group = parser.add_argument_group('mandatory arguments')
    for envname, attr in config_vars.items():
        if attr.get('required', False):
            _add_argument(mandatory_group, envname, attr)
        else:
            _add_argument(parser, envname, attr)

    common_config_vars['SERVICE_NAME']['default'] = service_name
    common_group = parser.add_argument_group('common options')
    for envname, attr in common_config_vars.items():
        _add_argument(common_group, envname, attr)
