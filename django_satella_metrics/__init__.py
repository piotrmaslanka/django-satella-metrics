import typing as tp
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from satella.time import measure
from satella.instrumentation.metrics import Metric, getMetric
__version__ = '0.1a1'


__all__ = ['DjangoSatellaMetricsMiddleware']


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

        self.get_response = get_response
        self.get_response_name = get_response.__module__ + '.' + get_response.__qualname__

    def __call__(self, request):
        with measure() as measurement:
            response = self.get_response(request)
        self.summary_metric.runtime(measurement(), view=self.get_response_name)
        self.histogram_metric.runtime(measurement(), view=self.get_response_name)
        self.request_code_metric.runtime(+1, status_code=response.status_code)
        return response

