# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'devices', views.DevicesView, base_name='device')

urlpatterns = [
    url(r'^iothings/', include([
        url(r'^ping/$', views.PingView.as_view(), name='ping'),
    ] + router.urls)),
    url(r'^status/', include('iot.health.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])
