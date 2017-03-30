# em_tools

collection of python tools for basic service setup

There are three areas addressed by this package:
* config - load configuration parameters either from env vars or cli. Load secrets from file if needed.
* logging - setup formatters and handler for console or syslog logging. It will also
    configure Sentry client, if required.
* metrics - create https://prometheus.io/ push task. It will periodically push service metrics
    to configured pushgateway. In sync mode, it will create thread. In async, it will create
    async Task for it.

## Config

### environment and command-line

All configuration is done via environment variables. Optionally, they can
be specified on command-line as well.

For example:
```
FOO=bar python example.py
```
is equivalent to
```
python example.py --FOO=bar
```

Option -h will provide help, which env variables are recognized.

### common config parameters

Some parameters are common for all services, so they are defined by this package.
They will be added to `argparse` as part of `setup_config()`/`basic_setup()` calls.

### secrets

If the string value of configuration parameter is `"secret:<name>"`
then `<name>` is considered to be a filename under `/run/secrets/` directory
For example, config parameter with
value `"secret:sentry_dsn"` will get its the value from the content
of `/run/secrets/sentry_dsn` file.

This feature if optional. You may still specify secrets by their verbatim value.

### in code

Service configuration parameters are defined in one dictionary, like:
```python
config_vars = {
    'DB_USER':      dict(default='example', help='database user (default "%(default)s")'),
    'DB_PASSWORD':  dict(default='example', secret=True, help='(secret) database password'),
    'DB_HOSTNAME':  dict(required=True, help='database hostname'),
    'DB_PORT':      dict(default='5432', help='database port (default "%(default)s")'),
}
```

Attributes correspond to arguments of `argparse`'s `add_argument()` call. There is one
additional attribute `secret` which will mark the parameter as containing secret.

## Logging

Logging is set either to console (default) or syslog. For syslog, SERVICE_NAME is used
as syslog_identifier.

We also setup Sentry client (raven) for logging of warnings and errors to Sentry.

## Metrics

For metrics we use Prometheus in push mode. Each service instance is responsible
for pushing out its metrics to configured Prometheus pushgateway.


## Examples

### simple sync service (python 2.x, 3.x)

See full example in `example.py`
```python
from em_tools import basic_setup

config_vars = {
    # put your service-specific parameters here
}

def main():
    config = basic_setup(service_name='example', config_vars=config_vars)
```

### explicit setup in sync service (python 2.x, 3.x)

```python
import argparse
from em_tools import setup_config, setup_logging, setup_metrics

config_vars = {
    # put your service-specific parameters here
}

def main():
    parser = argparse.ArgumentParser(usage='example.py [<option>..]')
    setup_config(parser, config_vars, service_name='example')
    config = parser.parse_args()
    setup_logging(config)
    setup_metrics(config)
```

### asyncio service (python 3.5+)

See full example in `aioexample.py`
```python
import asyncio
import argparse
from em_tools import setup_config, setup_logging
from em_tools.aiometrics import setup_metrics, shutdown_metrics

config_vars = {
    # put your service-specific parameters here
}

async def mainloop(config):
    pass

def main():
    parser = argparse.ArgumentParser(usage='aioexample.py [<option>..]')
    setup_config(parser, config_vars, service_name='aioexample')
    config = parser.parse_args()
    setup_logging(config)

    loop = asyncio.get_event_loop()
    pusher_task = setup_metrics(loop, config)
    loop.run_until_complete(mainloop(config))
    shutdown_metrics(loop, pusher_task)
```

### example help output

```bash
usage: example.py [<option>..]

This is a long description of the service. To configure it, you may specify
config parameters on command-line or env variables. Some parameters can
contain secrets. Their value may be specified as "secret:foo", in which case,
it will be read from /run/secrets/foo file.

optional arguments:
  -h, --help            show this help message and exit
  --DB_PASSWORD <str>   (secret) database password
  --DB_USER <str>       database user (default "example")
  --DB_PORT <str>       database port (default "5432")

mandatory arguments:
  --DB_HOSTNAME <str>   database hostname

common options:
  --SENTRY_DSN <str>    (secret) sentry DSN. If set, sentry logger will be
                        configured as well (default: unset)
  --LOG_TARGET <str>    where to send logs (console/syslog) (default: console)
  --SERVICE_NAME <str>  service name (default: "dummy")
  --TASK_SLOT <int>     task id within service (default: 1)
  --LOG_LEVEL <str>     logging verbosity: error/warning/info/debug (default:
                        info)
  --PROMETHEUS_HOST <str>
                        prometheus pushgateway hostname, non-empty value
                        enables pushing (default: "")
  --PROMETHEUS_PUSH_INTERVAL <int>
                        how often to push out metrics [s] (default: 10s)
```
