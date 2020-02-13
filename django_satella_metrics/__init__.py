import typing as tp
from django.utils.deprecation import MiddlewareMixin
from satella.time import measure
from satella.instrumentation.metrics import Metric, getMetric
__version__ = '0.1a1'


def get_satella_metrics(summary_metric: tp.Optional[Metric] = None,
                        histogram_metric: tp.Optional[Metric] = None,
                        request_code_metric: tp.Optional[Metric] = None):
    """
    Return a middleware class for usage in Django.

    :param summary_metric: summary metric to use. If not specified, default metric of
        django.summary will be used
    :param histogram_metric: histogram metric to use. If not specified, default metric of
        django.histogram will be used
    :param request_code_metric: request code metric to use. If not specified, default metric of
        django.request_codes will be used. Should be of type counter.
    :return:
    """

    class DjangoSatellaMetricsMiddleware(MiddlewareMixin):
        def __init__(self, get_response):
            self.get_response = get_response
            self.get_response_name = get_response.__module__ + '.' + get_response.__qualname__

        def __call__(self, request):
            with measure() as measurement:
                response = self.get_response(request)
            summary_metric.runtime(measurement(), view=self.get_response_name)
            histogram_metric.runtime(measurement(), view=self.get_response_name)
            request_code_metric.runtime(+1, status_code=response.status_code)
            return response

    return DjangoSatellaMetricsMiddleware

