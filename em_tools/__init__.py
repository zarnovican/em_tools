
import argparse

from .config import setup_config
from .log import setup_logging
from .metrics import setup_metrics


def basic_setup(service_name='dummy', usage=None, description=None, version=None, config_vars={}):
    """Setup cli args, logging and metrics in one go"""

    if usage is None:
        usage = '{} [<option>..]'.format(service_name)

    parser = argparse.ArgumentParser(usage=usage, description=description)
    setup_config(parser, config_vars, version=version)
    config = parser.parse_args()
    setup_logging(config)
    setup_metrics(config)
    return config
