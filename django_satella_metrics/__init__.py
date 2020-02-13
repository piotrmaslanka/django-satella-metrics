from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponse
from satella.time import measure
from satella.instrumentation.metrics import getMetric
from satella.instrumentation.metrics.exporters import metric_data_collection_to_prometheus

__version__ = '1.0'


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
            django_satella_metrics = settings.DJANGO_SATELLA_METRICS
            try:
                self.summary_metric = django_satella_metrics['summary_metric']
            except KeyError:
                self.summary_metric = getMetric('django.summary', 'summary')
            try:
                self.histogram_metric = django_satella_metrics['histogram_metric']
            except KeyError:
                self.histogram_metric = getMetric('django.histogram', 'histogram')
            try:
                self.status_codes_metric = django_satella_metrics['status_codes_metric']
            except KeyError:
                self.status_codes_metric = getMetric('django.status_codes', 'summary')
            self.monitor_metrics = settings.DJANGO_SATELLA_METRICS.get('monitor_metrics', False)
            self.url_getter = settings.DJANGO_SATELLA_METRICS.get('url_getter',
                                                                  lambda request: request.path)

        self.get_response = get_response

    def __call__(self, request):
        with measure() as measurement:
            response = self.get_response(request)
        if request.path != '/metrics':
            url = self.url_getter(request)
            self.summary_metric.runtime(measurement(), url=url)
            self.histogram_metric.runtime(measurement(), url=url)
            self.status_codes_metric.runtime(+1, status_code=response.status_code, url=url)
        return response


def export_metrics(request):
    """A Django view to output the metrics"""
    root_data = getMetric().to_metric_data()
    if hasattr(settings, 'DJANGO_SATELLA_METRICS'):
        root_data.add_labels(settings.DJANGO_SATELLA_METRICS.get('extra_labels', {}))
    return HttpResponse(metric_data_collection_to_prometheus(root_data))
