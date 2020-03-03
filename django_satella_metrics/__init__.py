import logging
logger = logging.getLogger(__name__)
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    logger.warning('You are using a very old version of Django. Please update')
    MiddlewareMixin = object

from django.conf import settings
from django.http import HttpResponse
from satella.time import measure
from satella.instrumentation.metrics import getMetric
from satella.instrumentation.metrics.exporters import metric_data_collection_to_prometheus

__version__ = '1.3'


__all__ = ['DjangoSatellaMetricsMiddleware', 'export_metrics', '__version__']


class DjangoSatellaMetricsMiddleware(MiddlewareMixin):
    """
    A middleware for measing Django calls using Satella's metrics.

    Make sure that this middleware launches first and exits last.

    This takes the following from settings
    """

    def __init__(self, get_response):
        if not hasattr(settings, 'DJANGO_SATELLA_METRICS'):
            self.summary_metric = getMetric('django.summary', 'summary')
            self.histogram_metric = getMetric('django.histogram', 'histogram')
            self.status_codes_metric = getMetric('django.status_codes', 'counter')
            self.monitor_metrics = False
            self.url_getter = lambda request: request.path
        else:
            def try_get(field_name, def_metric_name, def_metric_type):
                if field_name not in settings.DJANGO_SATELLA_METRICS:
                    setattr(self, field_name, getMetric(def_metric_name, def_metric_type))
                else:
                    setattr(self, field_name, settings.DJANGO_SATELLA_METRICS[field_name])

            try_get('summary_metric', 'django.summary', 'summary')
            try_get('histogram_metric', 'django.histogram', 'histogram')
            try_get('status_codes_metric', 'django.status_codes', 'counter')
            self.monitor_metrics = settings.DJANGO_SATELLA_METRICS.get('monitor_metrics', False)
            self.url_getter = settings.DJANGO_SATELLA_METRICS.get('url_getter',
                                                                  lambda request: request.path)

        self.get_response = get_response

    def process_request(self, request):
        request.metric_time_measurement = measure()
        request.metric_time_measurement.start()

    def process_response(self, request, response):
        measurement = request.metric_time_measurement
        measurement.stop()

        if request.path != '/metrics':
            url = self.url_getter(request)
            self.summary_metric.runtime(measurement(), url=url)
            self.histogram_metric.runtime(measurement(), url=url)
            self.status_codes_metric.runtime(+1, status_code=response.status_code, url=url)

        return response


def export_metrics(request):
    """A Django view to output the metrics"""
    root_data = getMetric().to_metric_data()
    for datum in root_data.values:
        if datum.internal:
            root_data.values.remove(datum)
    if hasattr(settings, 'DJANGO_SATELLA_METRICS'):
        root_data.add_labels(settings.DJANGO_SATELLA_METRICS.get('extra_labels', {}))
    return HttpResponse(metric_data_collection_to_prometheus(root_data))
