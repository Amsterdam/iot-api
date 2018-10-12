# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.utils import timezone
from rest_framework import views
from rest_framework.response import Response


class PingView(views.APIView):
    throttle_classes = ()
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        return Response({
            'date': timezone.now()
        })
