from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^$', 'service_status.views.index', name='status.service.index'),
    url(r'^celery/$', 'service_status.views.celery', name='status.service.celery'),
)
