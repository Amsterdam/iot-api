from django.urls import reverse
from rest_framework.test import APITestCase


class PingTestCase(APITestCase):
    def test_index_pages(self):
        url = reverse('ping')
        response = self.client.get(url)

        self.assertEqual(
            response.status_code, 200, 'Wrong response code for {}'.format(url)
        )
