
import aiohttp
import asyncio
import logging

from prometheus_client import CollectorRegistry, generate_latest

from .metrics import registry


async def prometheus_pusher(url, job, interval):
    """async task to push metrics to prometheus pushgateway"""

    try:
        pushgateway_uri = '{}/metrics/job/{}'.format(url.rstrip('/'), job)
        logging.info('Starting prometheus_pusher loop, url={}, interval={}s'.format(pushgateway_uri, interval))
        async with aiohttp.ClientSession() as session:
            while True:
                await asyncio.sleep(interval)
                data = generate_latest(registry)
                try:
                    async with session.put(pushgateway_uri, data=data) as resp:
                        if resp.status != 202:
                            logging.warning('Prometheus pushgateway response was {}'.format(resp.status))
                except aiohttp.errors.ClientError as e:
                    logging.warning('Prometheus push failed: {}'.format(str(e)))
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.exception('Prometheus pusher crashed: {}'.format(str(e)))


def setup_metrics(loop, config):
    """Create and return asyncio.Task to push prometheus metrics

    If metrics pushing is not enabled, it will return None"""

    if not config.METRICS:
        logging.info('Prometheus metrics pushing is disabled, which is ok.')
        return None

    url = 'http://{}:9091'.format(config.METRICS_HOST)
    return loop.create_task(prometheus_pusher(
        url=url, job=config.SERVICE_NAME, interval=config.METRICS_INTERVAL))


def shutdown_metrics(loop, pusher_task):
    """Gracefully shutdown the task (cancel and await)"""

    if pusher_task:
        pusher_task.cancel()
        loop.run_until_complete(pusher_task)
