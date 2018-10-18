# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datapunt_api.rest import DatapuntViewSet
from django.utils import timezone
from rest_framework import views
from rest_framework.response import Response

from .models import Device
from .serializers import DeviceSerializer


class PingView(views.APIView):
    throttle_classes = ()
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        return Response({
            'date': timezone.now()
        })


class DevicesView(DatapuntViewSet):
    """
    A view that will return the iot devices
    """

    queryset = Device.objects.all()

    serializer_class = DeviceSerializer
    serializer_detail_class = DeviceSerializer

    def __init__(self, *args, **kwargs):
        super(DevicesView, self).__init__(**kwargs)
