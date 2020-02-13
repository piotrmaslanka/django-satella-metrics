import typing as tp
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponse
from satella.time import measure
from satella.instrumentation.metrics import Metric, getMetric
from satella.instrumentation.metrics.exporters import metric_data_collection_to_prometheus

__version__ = '0.1a1'


__all__ = ['DjangoSatellaMetricsMiddleware', 'export_metrics']


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

        self.get_response = get_response

    def __call__(self, request):
        with measure() as measurement:
            response = self.get_response(request)
        if request.path != '/metrics':
            self.summary_metric.runtime(measurement(), url=request.path)
            self.histogram_metric.runtime(measurement(), url=request.path)
            self.status_codes_metric.runtime(+1, status_code=response.status_code, url=request.path)
        return response


def export_metrics(request):
    """A Django view to output the metrics"""
    root_data = getMetric().to_metric_data()
    if hasattr(settings, 'DJANGO_SATELLA_METRICS'):
        root_data.add_labels(settings.DJANGO_SATELLA_METRICS.get('extra_labels', {}))
    return HttpResponse(metric_data_collection_to_prometheus(root_data))
