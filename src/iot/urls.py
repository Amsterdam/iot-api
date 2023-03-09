# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from . import auth, views

urlpatterns = [
    # path(r'', views.PingView.as_view(), name='ping'),
    path(r'status/', include('iot.health.urls')),
]


class IoTRouter(DefaultRouter):
    APIRootView = views.IotRootView


if settings.API_ENABLED:
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

    # Swagger
    urlpatterns.extend(
        [
            path(settings.API_PATH, include((router.urls, 'api'))),
        ]
    )
    urlpatterns.extend(
        [
            re_path(
                r'swagger(?P<format>\.json|\.yaml)',
                schema_view.without_ui(cache_timeout=0),
                name='schema-json',
            ),
            path(
                r'swagger/',
                schema_view.with_ui('swagger', cache_timeout=0),
                name='schema-swagger-ui',
            ),
        ]
    )

# Admin
if settings.ADMIN_ENABLED:
    urlpatterns.extend(
        [
            path('admin/login/', auth.oidc_login),
            path(settings.ADMIN_PATH, admin.site.urls),
            path(r'oidc/', include('mozilla_django_oidc.urls')),
        ]
    )

# if settings.DEBUG:
# import debug_toolbar

# urlpatterns.extend(
#     [
#         path(r'__debug__/', include(debug_toolbar.urls)),
#     ]
# )

admin.autodiscover()
