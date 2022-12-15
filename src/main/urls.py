from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('iothings/', include('iot.urls'))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend(
        [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    )

admin.autodiscover()
