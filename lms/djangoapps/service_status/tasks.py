import time

from djcelery import celery


@celery.task
def delayed_ping(value, delay):
    if value == 'ping':
        result = 'pong'
    else:
        result = 'got: {0}'.format(value)

    time.sleep(delay)

    return result
