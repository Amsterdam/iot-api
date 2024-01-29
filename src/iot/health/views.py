import logging

from django.db import connection
from django.http import HttpResponse
from rest_framework import status

log = logging.getLogger(__name__)


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('select 1')
            assert cursor.fetchone()
    except Exception:
        log.exception('Database connectivity failed')
        return HttpResponse(
            'Database connectivity failed',
            content_type='text/plain',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return HttpResponse(
        'Connectivity OK',
        content_type='text/plain',
        status=status.HTTP_200_OK,
    )
