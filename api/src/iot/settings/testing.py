from iot.settings.base import *

SECRET_KEY = 'insecure'
CELERY_TASK_ALWAYS_EAGER = True
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
TEST_LOGIN = 'iot.admin@amsterdam.nl'
SITE_DOMAIN = 'localhost:8000'
