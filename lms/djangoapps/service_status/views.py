import json
import time

from django.http import HttpResponse

from dogapi import dog_stats_api

from service_status import tasks


def index(request):
    return HttpResponse()


@dog_stats_api.timed('status.service.celery')
def celery(request):
    """
    A Simple view that checks if the application can talk to the celery workers
    """
    start = time.time()
    args = ('ping', 0.1)
    result = tasks.delayed_ping.apply_async(args)

    # Wait until we get the result
    value = result.get(timeout=4.0)

    output = {
        'task_id': result.id,
        'value': value,
        'time': time.time() - start
    }

    return HttpResponse(json.dumps(output, indent=4))
