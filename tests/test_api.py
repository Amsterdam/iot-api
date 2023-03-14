from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from iot.factories import DeviceFactory
from iot.serializers import DeviceJsonSerializer
from iot.views import DevicesViewSet


class DeviceTestCase(APITestCase):
    def test_get(self):
        DeviceFactory.create()
        url = reverse('api:device-list')
        response = self.client.get(url)
        actual = response.json()['results'][0]
        expected = DeviceJsonSerializer(DevicesViewSet.queryset[0]).data
        assert actual == expected
