import os
import sys

# This import enables the OIDC login. Without this import, users cannot log in to the admin portal!
# The "noqa" comment prevents Flake from removing this import as an unused import.
from keycloak_oidc.default_settings import *  # noqa

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

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

# Django security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

## KEYCLOAK ##
# External identity provider settings (Keycloak)
LOGIN_REDIRECT_URL = "/iothings/admin/"

OIDC_DEFAULT_URL = (
    'https://iam.amsterdam.nl/auth/realms/datapunt-ad-acc/protocol/openid-connect'
)

OIDC_RP_CLIENT_ID = os.environ['OIDC_RP_CLIENT_ID']
OIDC_RP_CLIENT_SECRET = os.environ['OIDC_RP_CLIENT_SECRET']
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get(
    'OIDC_OP_AUTHORIZATION_ENDPOINT', f'{OIDC_DEFAULT_URL}/auth'
)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get(
    'OIDC_OP_TOKEN_ENDPOINT', f'{OIDC_DEFAULT_URL}/token'
)
OIDC_OP_USER_ENDPOINT = os.environ.get(
    'OIDC_OP_USER_ENDPOINT', f'{OIDC_DEFAULT_URL}/userinfo'
)
OIDC_OP_JWKS_ENDPOINT = os.environ.get(
    'OIDC_OP_JWKS_ENDPOINT', f'{OIDC_DEFAULT_URL}/certs'
)
OIDC_OP_LOGOUT_ENDPOINT = LOGOUT_REDIRECT_URL = os.environ.get(
    'OIDC_OP_LOGOUT_ENDPOINT', f'{OIDC_DEFAULT_URL}/logout'
)
LOGIN_REDIRECT_URL_FAILURE = '/iothings/static/403.html'

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
]

THIRD_PARTY_APPS = [
    'django_extensions',
    'django_filters',
    'datapunt_api',
    'drf_yasg',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rest_framework_gis',
    'keycloak_oidc',  # load after django.contrib.auth!
    'leaflet',
]

DEBUG_APPS = ['debug_toolbar']


# Apps specific for this project go here.
LOCAL_APPS = ['main', 'iot', 'health']

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
]

DEBUG_MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'pyinstrument.middleware.ProfilerMiddleware',
]

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
    'iot.auth.OIDCAuthenticationBackend',
]

SENSOR_REGISTER_ADMIN_ROLE_NAME = os.environ.get('SENSOR_REGISTER_ADMIN_ROLE_NAME', 'x')

ROOT_URLCONF = "main.urls"
WSGI_APPLICATION = "main.wsgi.application"

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

SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = 10_000

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("DATABASE_NAME", "dev"),
        "USER": os.getenv("DATABASE_USER", "dev"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "dev"),
        "HOST": os.getenv("DATABASE_HOST", "database"),
        "CONN_MAX_AGE": 20,
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    },
}

# Internationalization
LANGUAGE_CODE = 'nl-NL'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) and media files
STATIC_URL = '/iothings/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
MEDIA_URL = '/iothings/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')


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
        'console': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}
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
        },
    },
    'loggers': {
        'iot': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': os.getenv(
                'DJANGO_LOG_LEVEL', 'ERROR' if 'pytest' in sys.argv[0] else 'INFO'
            ).upper(),
            'propagate': False,
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
    DEFAULT_PAGINATION_CLASS=('datapunt_api.pagination.HALPagination',),
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
    DEFAULT_THROTTLE_RATES={'nouser': '60/hour'},
)

ATLAS_POSTCODE_SEARCH = 'https://api.data.amsterdam.nl/atlas/search/postcode'
ATLAS_ADDRESS_SEARCH = 'https://api.data.amsterdam.nl/atlas/search/adres'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# In the IPROX formuler the user can register 5 sensors at a time
IPROX_NUM_SENSORS = 5
IPROX_SEPARATOR = ';'
