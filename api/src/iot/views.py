# -*- coding: utf-8 -*-

from datapunt_api.rest import DatapuntViewSet
from django.utils import timezone
from rest_framework import routers, views
from rest_framework.response import Response

from .models import Device2
from .serializers import Device2Serializer


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


class DevicesViewSet(DatapuntViewSet):
    """
    A view that will return the iot devices and makes it possible to post new ones
    """
    queryset = (
        Device2.objects.all()
        .select_related('type', 'owner')
        .prefetch_related('themes', 'regions', "observation_goals", "projects")
        .order_by('id')
    )
    serializer_class = Device2Serializer
    serializer_detail_class = Device2Serializer

    http_method_names = ['get']
