# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datapunt_api.rest import DatapuntViewSetWritable
from django.utils import timezone
from rest_framework import routers, views
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from iot.models import Device
from iot.serializers import DeviceSerializer, IotContactSerializer


class IotRootView(routers.APIRootView):
    """
    IoT Devices in the city are shown here as a list

    [github/amsterdam/afvalcontainers](https://github.com/Amsterdam/iot-api)

    [Author: David van Buiten](https://github.com/vanbuiten/)
    """


class PingView(views.APIView):
    throttle_classes = ()
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        return Response({
            'date': timezone.now()
        })


class DevicesViewSet(DatapuntViewSetWritable):
    """
    A view that will return the iot devices and makes it possible to post new ones
    """

    queryset = Device.objects.all().select_related('owner', 'contact').prefetch_related('types').order_by('id')

    serializer_class = DeviceSerializer
    serializer_detail_class = DeviceSerializer

    http_method_names = ['post', 'list', 'get']


class ContactViewSet(CreateModelMixin, GenericViewSet):
    queryset = Device.objects.none()
    serializer_class = IotContactSerializer
    pagination_class = None
