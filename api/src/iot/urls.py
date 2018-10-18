# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^iothings/', include([
        url(r'^ping/$', views.PingView.as_view(), name='ping'),
    ])),
    url(r'^status/', include('iot.health.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])
