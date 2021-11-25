import os

from keycloak_oidc.default_settings import *

from .settings_databases import (OVERRIDE_HOST_ENV_VAR, OVERRIDE_PORT_ENV_VAR,
                                 LocationKey, get_database_key,
                                 get_docker_host)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Django settings
INSECURE_SECRET_KEY = 'insecure'
SECRET_KEY = os.getenv('SECRET_KEY', INSECURE_SECRET_KEY)
DEBUG = SECRET_KEY == INSECURE_SECRET_KEY

ALLOWED_HOSTS = [
    'api.data.amsterdam.nl',
    'acc.api.data.amsterdam.nl',

    # Currently this is needed because the deployment process checks the health endpoint with a
    # request to localhost:port.
    'localhost',
    '127.0.0.1',
    '*',
]

INTERNAL_IPS = ('127.0.0.1', '0.0.0.0')
CORS_ORIGIN_ALLOW_ALL = True

DATAPUNT_API_URL = os.getenv('DATAPUNT_API_URL', 'https://api.data.amsterdam.nl/')

KEYCLOAK_SLIMMEAPPARATEN_WRITE_PERMISSION_NAME = "slim_app_w"

AMSTERDAM_PRIVACY_MAP_EMAIL_ADDRESS = os.environ['AMSTERDAM_PRIVACY_MAP_EMAIL_ADDRESS']

# Django security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

## KEYCLOAK ##
# External identity provider settings (Keycloak)
OIDC_RP_CLIENT_ID = os.environ['OIDC_RP_CLIENT_ID']
OIDC_RP_CLIENT_SECRET = os.environ['OIDC_RP_CLIENT_SECRET']
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT',
    'https://iam.amsterdam.nl/auth/realms/datapunt-acc/protocol/openid-connect/auth')
OIDC_OP_TOKEN_ENDPOINT = os.getenv('OIDC_OP_TOKEN_ENDPOINT',
    'https://iam.amsterdam.nl/auth/realms/datapunt-acc/protocol/openid-connect/token')
OIDC_OP_USER_ENDPOINT = os.getenv('OIDC_OP_USER_ENDPOINT',
    'https://iam.amsterdam.nl/auth/realms/datapunt-acc/protocol/openid-connect/userinfo')
OIDC_OP_JWKS_ENDPOINT = os.getenv('OIDC_OP_JWKS_ENDPOINT',
    'https://iam.amsterdam.nl/auth/realms/datapunt-acc/protocol/openid-connect/certs')
OIDC_OP_LOGOUT_ENDPOINT = os.getenv('OIDC_OP_LOGOUT_ENDPOINT',
    'https://iam.amsterdam.nl/auth/realms/datapunt-acc/protocol/openid-connect/logout')
LOGIN_REDIRECT_URL = "/iothings/devices/"
LOGOUT_REDIRECT_URL = "/iothings/devices/"


# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
)

THIRD_PARTY_APPS = (
    'django_extensions',
    'django_filters',

    'djcelery_email',

    'datapunt_api',

    'drf_yasg',
    'raven.contrib.django.raven_compat',

    'rest_framework',
    'rest_framework_gis',

    'keycloak_oidc',  # load after django.contrib.auth!
    'leaflet'
)

DEBUG_APPS = (
    'debug_toolbar',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'iot',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
)

DEBUG_MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

if DEBUG:
    INSTALLED_APPS += DEBUG_APPS
    MIDDLEWARE += DEBUG_MIDDLEWARE
    CORS_ORIGIN_ALLOW_ALL = True
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]

AUTHENTICATION_BACKENDS = [
    'keycloak_oidc.auth.OIDCAuthenticationBackend',
]

SENSOR_REGISTER_ADMIN_ROLE_NAME = os.environ.get(
    'SENSOR_REGISTER_ADMIN_ROLE_NAME',
    'sensoren-register-admin',
)

ROOT_URLCONF = "iot.urls"
WSGI_APPLICATION = "iot.wsgi.application"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        },
    }
]

# Database
DATABASE_OPTIONS = {
    LocationKey.docker: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'iothings'),
        'USER': os.getenv('DATABASE_USER', 'iothings'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': 'database',
        'PORT': '5432',
    },
    LocationKey.local: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'iothings'),
        'USER': os.getenv('DATABASE_USER', 'iothings'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': get_docker_host(),
        'PORT': '5432',
    },
    LocationKey.override: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'iothings'),
        'USER': os.getenv('DATABASE_USER', 'iothings'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv(OVERRIDE_HOST_ENV_VAR),
        'PORT': os.getenv(OVERRIDE_PORT_ENV_VAR, '5432'),
    },
}
DATABASES = {
    'default': DATABASE_OPTIONS[get_database_key()]
}

# Internationalization
LANGUAGE_CODE = 'nl-NL'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) and media files
STATIC_URL = '/iothings/static/'
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'static')
MEDIA_URL = '/iothings/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'media')

# Object store / Swift
if os.getenv('SWIFT_ENABLED', 'false') == 'true':
    DEFAULT_FILE_STORAGE = 'swift.storage.SwiftStorage'
    SWIFT_USERNAME = os.getenv('SWIFT_USERNAME')
    SWIFT_PASSWORD = os.getenv('SWIFT_PASSWORD')
    SWIFT_AUTH_URL = os.getenv('SWIFT_AUTH_URL')
    SWIFT_TENANT_ID = os.getenv('SWIFT_TENANT_ID')
    SWIFT_TENANT_NAME = os.getenv('SWIFT_TENANT_NAME')
    SWIFT_REGION_NAME = os.getenv('SWIFT_REGION_NAME')
    SWIFT_CONTAINER_NAME = os.getenv('SWIFT_CONTAINER_NAME')
    SWIFT_TEMP_URL_KEY = os.getenv('SWIFT_TEMP_URL_KEY')
    SWIFT_USE_TEMP_URLS = True

# The following JWKS data was obtained in the authz project :  jwkgen -create -alg ES256   # noqa
# This is a test public/private key def and added for testing .
JWKS_TEST_KEY = """
    {
        "keys": [
            {
                "kty": "EC",
                "key_ops": [
                    "verify",
                    "sign"
                ],
                "kid": "2aedafba-8170-4064-b704-ce92b7c89cc6",
                "crv": "P-256",
                "x": "6r8PYwqfZbq_QzoMA4tzJJsYUIIXdeyPA27qTgEJCDw=",
                "y": "Cf2clfAfFuuCB06NMfIat9ultkMyrMQO9Hd2H7O9ZVE=",
                "d": "N1vu0UQUp0vLfaNeM0EDbl4quvvL6m_ltjoAXXzkI3U="
            }
        ]
    }
"""

DATAPUNT_AUTHZ = {
    'JWKS': os.getenv('PUB_JWKS', JWKS_TEST_KEY),
    'ALWAYS_OK': False,
}

# Django cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Sentry logging
RAVEN_CONFIG = {
    'dsn': os.getenv('SENTRY_RAVEN_DSN'),
}

# Django Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'sentry'],
    },
    'formatters': {
        'console': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        }
    },
    'loggers': {
        'iot': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': True,
        },
        'django': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': True,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },

        # Debug all batch jobs
        'doc': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'index': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'search': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'elasticsearch': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'urllib3': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'factory.containers': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'factory.generate': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'requests.packages.urllib3.connectionpool': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },

        # Log all unhandled exceptions
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# Django REST framework settings
REST_FRAMEWORK = dict(
    PAGE_SIZE=100,
    MAX_PAGINATE_BY=100,
    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    DEFAULT_AUTHENTICATION_CLASSES=(
        'mozilla_django_oidc.contrib.drf.OIDCAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    DEFAULT_PAGINATION_CLASS=(
        'datapunt_api.pagination.HALPagination',
    ),
    DEFAULT_RENDERER_CLASSES=(
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    DEFAULT_FILTER_BACKENDS=(
        # 'rest_framework.filters.SearchFilter',
        # 'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    COERCE_DECIMAL_TO_STRING=True,
    DEFAULT_THROTTLE_CLASSES=(
        # Currently no default throttle class
    ),
    DEFAULT_THROTTLE_RATES={
        'nouser': '60/hour'
    },
)


# Mail
# EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'djcelery_email.backends.CeleryEmailBackend')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.getenv('EMAIL_PORT', 465)
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', False)
if not EMAIL_USE_TLS:
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', True)

EMAIL = 'registerslimmeapparaten@amsterdam.nl'
NOREPLY = 'no-reply@amsterdam.nl'

# This should be set to 'django.core.mail.backends.smtp.EmailBackend' for acc/prod
CELERY_EMAIL_BACKEND = os.getenv('CELERY_EMAIL_BACKEND',
                                 'django.core.mail.backends.smtp.EmailBackend')


# Celery settings
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'iothings')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'insecure')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', 'vhost')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL',
                              f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}'
                              f'@{RABBITMQ_HOST}/{RABBITMQ_VHOST}')

CELERY_EMAIL_TASK_CONFIG = {
    'queue': 'email',
    'ignore_result': True,
    'rate_limit': '50/m',  # * CELERY_EMAIL_CHUNK_SIZE (default: 10)
}

ATLAS_POSTCODE_SEARCH = 'https://api.data.amsterdam.nl/atlas/search/postcode'
ATLAS_ADDRESS_SEARCH = 'https://api.data.amsterdam.nl/atlas/search/adres'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# In the IPROX formuler the user can register 5 sensors at a time
IPROX_NUM_SENSORS = 5
