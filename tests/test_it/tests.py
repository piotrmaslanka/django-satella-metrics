from django.test import TestCase


class TestExporter(TestCase):
    def test_metrics(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        resp = self.client.get('/metrics')
        self.assertIn(b'service_name="test"', resp.content)
