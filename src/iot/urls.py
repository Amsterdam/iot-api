# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from . import auth, views


class IoTRouter(DefaultRouter):
    APIRootView = views.IotRootView


router = IoTRouter()
router.register(r'devices', views.DevicesViewSet, basename='device')


schema_view = get_schema_view(
    openapi.Info(
        title='IoT API',
        default_version='v1',
        description='IoT Devices in Amsterdam',
        terms_of_service='https://data.amsterdam.nl/',
        contact=openapi.Contact(email='datapunt@amsterdam.nl'),
        license=openapi.License(name='CC0 1.0 Universal'),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    re_path(
        r'^iothings/',
        include(
            router.urls
            + [
                re_path(
                    r'^swagger(?P<format>\.json|\.yaml)$',
                    schema_view.without_ui(cache_timeout=None),
                    name='schema-json',
                ),
                re_path(
                    r'^swagger/$',
                    schema_view.with_ui('swagger', cache_timeout=None),
                    name='schema-swagger-ui',
                ),
                re_path(r'^ping/$', views.PingView.as_view(), name='ping'),
                re_path(r'^oidc/', include('keycloak_oidc.urls')),
                path('admin/login/', auth.oidc_login),
                path('admin/', admin.site.urls),
            ]
        ),
    ),
    re_path(r'^status/', include('health.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend(
        [
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    )

admin.autodiscover()
