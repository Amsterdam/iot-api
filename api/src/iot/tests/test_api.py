from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from iot.factories import Device2Factory
from iot.serializers import Device2Serializer


class PingTestCase(APITestCase):
    def test_index_pages(self):
        url = reverse('ping')
        response = self.client.get(url)

        self.assertEqual(
            status.HTTP_200_OK, response.status_code, 'Wrong response code for {}'.format(url)
        )


class DeviceTestCase(APITestCase):
    def test_get(self):
        device = Device2Factory.create()
        url = reverse('device-list')
        response = self.client.get(url)
        actual = response.json()['results'][0]
        expected = Device2Serializer(device).data
        assert actual == expected
