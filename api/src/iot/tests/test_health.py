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
    @mock.patch('iot.health.views.log')
    def test_health_not_ok(self, log, mocked_connection):

        with mocked_connection.cursor() as mocked_cursor:
            mocked_cursor.execute.side_effect = Error()

        url = reverse('health')
        response = self.client.get(url)

        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        log.exception.assert_called()
