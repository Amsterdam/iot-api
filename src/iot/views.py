# -*- coding: utf-8 -*-

from datapunt_api.rest import DatapuntViewSet
from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models import Aggregate, Min
from django.db.models.expressions import F, Func
from django.db.models.functions import Cast, JSONObject
from django.forms import BooleanField, IntegerField
from django.utils import timezone
from rest_framework import routers, views
from rest_framework.response import Response

from .models import Device, DeviceJson
from .serializers import DeviceJsonSerializer


class IotRootView(routers.APIRootView):
    """
    IoT Devices in the city are shown here as a list

    [github/amsterdam/iot-api](https://github.com/Amsterdam/iot-api)

    [Author: Gemeente Amsterdam](https://github.com/amsterdam/)
    """


class PingView(views.APIView):
    throttle_classes = ()
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        return Response({'date': timezone.now()})


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
    queryset = DeviceJson.objects.raw(
        """
        SELECT "iot_device"."id" AS "id",
               JSONB_AGG(DISTINCT "iot_theme"."name") AS "themes",
               JSONB_AGG(DISTINCT JSONB_BUILD_OBJECT(
                   'id', "iot_observationgoal"."id",
                   'observation_goal', "iot_observationgoal"."observation_goal",
                   'legal_ground', "iot_legalground"."name",
                   'privacy_declaration', "iot_observationgoal"."privacy_declaration"
               )) AS "observation_goals",
               JSONB_AGG(DISTINCT "iot_project"."path") FILTER (WHERE "iot_project"."path" is not null) AS "project_paths",
               JSONB_AGG(DISTINCT "iot_region"."name") FILTER (WHERE "iot_region"."name" is not null) AS "regions",
               JSONB_BUILD_OBJECT(
                   'name', "iot_person"."name",
                   'email', "iot_person"."email",
                   'organisation', "iot_person"."organisation"
               ) AS "owner",
               JSONB_BUILD_OBJECT(
                   'latitude', ST_Y("iot_device"."location"),
                   'longitude', ST_X("iot_device"."location")
               ) AS "location",
               "iot_device"."active_until",
               "iot_device"."contains_pi_data",
               "iot_device"."datastream",
               "iot_device"."location_description",
               "iot_device"."reference",
               "iot_type"."name" as "type"
        FROM "iot_device"
             LEFT OUTER JOIN "iot_device_themes"
                             ON ("iot_device"."id" = "iot_device_themes"."device_id")
             LEFT OUTER JOIN "iot_theme"
                             ON ("iot_device_themes"."theme_id" = "iot_theme"."id")
             LEFT OUTER JOIN "iot_device_observation_goals"
                             ON ("iot_device"."id" = "iot_device_observation_goals"."device_id")
             LEFT OUTER JOIN "iot_observationgoal"
                             ON ("iot_device_observation_goals"."observationgoal_id" = "iot_observationgoal"."id")
             LEFT OUTER JOIN "iot_legalground"
                             ON ("iot_observationgoal"."legal_ground_id" = "iot_legalground"."id")
             LEFT OUTER JOIN "iot_device_projects"
                             ON ("iot_device"."id" = "iot_device_projects"."device_id")
             LEFT OUTER JOIN "iot_project"
                             ON ("iot_device_projects"."project_id" = "iot_project"."id")
             LEFT OUTER JOIN "iot_device_regions"
                             ON ("iot_device"."id" = "iot_device_regions"."device_id")
             LEFT OUTER JOIN "iot_region"
                             ON ("iot_device_regions"."region_id" = "iot_region"."id")
             INNER JOIN     "iot_person"
                             ON ("iot_device"."owner_id" = "iot_person"."id")
             INNER JOIN     "iot_type"
                             ON ("iot_device"."type_id" = "iot_type"."id")
        WHERE "iot_device"."location" IS NOT NULL
        GROUP BY "iot_device"."id", "iot_person"."id", "iot_type"."name"
        ORDER BY "iot_device"."id"
    """
    )
    serializer_class = DeviceJsonSerializer
    serializer_detail_class = DeviceJsonSerializer

    http_method_names = ['get']
