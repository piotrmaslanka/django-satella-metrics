from setuptools import setup, find_packages

from django_satella_metrics import __version__


setup(keywords=['django', 'metrics', 'instrumentation', 'monitoring', 'server', 'satella'],
      packages=find_packages(include=['django_satella_metrics', 'django_satella_metrics.*']),
      version=__version__,
      install_requires=[
            'django', 'satella'
      ],
      tests_require=[
          "nose2", "mock", "coverage", "nose2[coverage_plugin]"
      ],
      test_suite='nose2.collector.collector',
      python_requires='!=2.7.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
      )
