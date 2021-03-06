django-satella-metrics
======================
[![Build Status](https://travis-ci.org/piotrmaslanka/django-satella-metrics.svg)](https://travis-ci.org/piotrmaslanka/django-satella-metrics)
[![Test Coverage](https://api.codeclimate.com/v1/badges/34b392b61482d98ad3f0/test_coverage)](https://codeclimate.com/github/piotrmaslanka/django-satella-metrics/test_coverage)
[![Code Climate](https://codeclimate.com/github/piotrmaslanka/django-satella-metrics/badges/gpa.svg)](https://codeclimate.com/github/piotrmaslanka/django-satella-metrics)
[![Issue Count](https://codeclimate.com/github/piotrmaslanka/django-satella-metrics/badges/issue_count.svg)](https://codeclimate.com/github/piotrmaslanka/django-satella-metrics)
[![PyPI](https://img.shields.io/pypi/pyversions/django-satella-metrics.svg)](https://pypi.python.org/pypi/django-satella-metrics)
[![PyPI version](https://badge.fury.io/py/django-satella-metrics.svg)](https://badge.fury.io/py/django-satella-metrics)
[![PyPI](https://img.shields.io/pypi/implementation/django-satella-metrics.svg)](https://pypi.python.org/pypi/django-satella-metrics)

django-satella-metrics is a library to measure [Django's](https://github.com/django/django) 
requests using [Satella's](https://github.com/piotrmaslanka/satella) metrics

See [LICENSE](LICENSE) for text of the license. This library may contain
code taken from elsewhere on the internets, so this is copyright (c) respective authors.

As far as compatible Djangos are considered: This has been tested as early as Django 1.8 with Python 3.6
and as late as Django 3.0.3 with Python 3.8. Enjoy!

# Usage

First, add the following to your `MIDDLEWARE` (or `MIDDLEWARE_CLASSES`):
`'django_satella_metrics.DjangoSatellaMetricsMiddleware'`

Define the following in your settings:

```python
from satella.instrumentation.metrics import getMetric
DJANGO_SATELLA_METRICS = {
    'summary_metric': getMetric('django.summary', 'summary'),
    'histogram_metric': getMetric('django.histogram', 'histogram'),
    'status_codes_metric': getMetric('django.status_codes', 'counter')
}
```

Or pass any other metrics that you'd like. This is the default configuration, so if you pass nothing it will be 
as if you passed the listed code.

## Extra configuration

If you want URL readed from the request in a different way than reading URL, you can define a key called `url_getter`.
This should contain a callable that accepts a single argument, the request passed, and return a str, the URL to use.

Additionally, if you want the Prometheus exporter to add extra labels to your exported metrics, you can add a key to
the config of name `extra_labels` which will contain a dict with the labels to add, eg.

```python
DJANGO_SATELLA_METRICS = {
    'extra_labels': {
        'service_name': 'my_service',
        'instance': 1
    },
    'monitor_metrics': False
}
```

If you specify `monitor_metrics`, which is a bool, to be True, then `/metrics` endpoint will also be
considered during monitoring.

## Exporting from the same server

If you want to export metrics to Prometheus using Django, here you go. Just add following rule to your `urlpatterns`:

```python
from django_satella_metrics import export_metrics

urlpatterns = [
    ... ,
    path('metrics', export_metrics),
    ...
]
```

## External Prometheus server

If you want to set up an external Prometheus server, use the following snippet:

```python
from satella.instrumentation.metrics.exporters import PrometheusHTTPExporterThread
phet = PrometheusHTTPExporterThread('0.0.0.0', 8080, {'service_name': 'my_service'})
phet.start()
```
 