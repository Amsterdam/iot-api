# -*- coding: utf-8 -*-

from datapunt_api.rest import DatapuntViewSet
from django.contrib.postgres.aggregates import ArrayAgg, JSONBAgg
from django.db.models.expressions import F, Func
from django.db.models.functions import JSONObject
from django.utils import timezone
from rest_framework import routers, views
from rest_framework.response import Response

from .models import Device2
from .serializers import DeviceJsonSerializer


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
    A view that will return the iot devices
    """
    # Because there a lots of ManyToMany relationships even with django's
    # prefetch_related we end up with terrible performance. Particularly
    # since the front end tries to load all sensors at once. But we can
    # use the postgres specific aggregations to build this json objects
    # we need in SQL, meaning we can retrieve all the necessary data in
    # one query, this gives a nice 90% speedup.
    queryset = (
        Device2.objects.all()
        .annotate(_themes=ArrayAgg('themes__name'))
        .annotate(_observation_goals=JSONBAgg('observation_goals__observation_goal'))
        .annotate(_project_paths=JSONBAgg('projects__path'))
        .annotate(_regions=JSONBAgg('regions__name'))
        .annotate(_owner=JSONObject(
            name=F('owner__name'),
            email=F('owner__email'),
            organisation=F('owner__organisation'),
        ))
        .annotate(_location=JSONObject(
            latitude=Func('location', function='ST_Y'),
            longitude=Func('location', function='ST_X'),
        ))
        .values(
            "id",
            "active_until",
            "contains_pi_data",
            "datastream",
            "location_description",
            "reference",
            "type__name",
            "_regions",
            "_location",
            "_owner",
            "_observation_goals",
            "_themes",
            "_project_paths",
        )
        .order_by('id')
    )
    serializer_class = DeviceJsonSerializer
    serializer_detail_class = DeviceJsonSerializer

    http_method_names = ['get']
