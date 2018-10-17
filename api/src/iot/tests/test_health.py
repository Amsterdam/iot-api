from unittest import mock

from django.db import Error
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthTestCase(APITestCase):
    def test_health_ok(self):
        url = reverse('health')
        response = self.client.get(url)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

    @mock.patch('iot.health.views.connection')
    def test_health_not_ok(self, mocked_connection):
        mocked_cursor = mock.MagicMock()
        mocked_cursor.execute.side_effect = Error()
        mocked_connection.cursor.return_value.__enter__.return_value = mocked_cursor

        url = reverse('health')
        response = self.client.get(url)

        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
