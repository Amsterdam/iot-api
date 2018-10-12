from iot.settings.base import *

SECRET_KEY = 'insecure'
DEBUG = True

ALLOWED_HOSTS = ['*']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
