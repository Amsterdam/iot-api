import os
import sys
from urllib.parse import urljoin

import sentry_sdk
from opencensus.trace import config_integration
from sentry_sdk.integrations.django import DjangoIntegration

from .azure_settings import Azure

azure = Azure()

# This import enables the OIDC login. Without this import, users cannot log in to the admin portal!
# The "noqa" comment prevents Flake from removing this import as an unused import.
from keycloak_oidc.default_settings import *  # noqa

config_integration.trace_integrations(['requests', 'logging', 'postgresql'])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']
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
DEFAULT_IMPORT_TIMEOUT = 5

DATAPUNT_API_URL = os.getenv('DATAPUNT_API_URL', 'https://api.data.amsterdam.nl/')

# Django security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


# Admin
def make_url_path(url_path):
    """
    url paths should have trailing slash, unless its for the root
    """
    return (url_path.strip().strip('/') + '/').lstrip('/')


API_ENABLED = os.getenv('API_ENABLED', 'true').lower() == 'true'
API_PATH = make_url_path(os.getenv('API_PATH', 'api'))

ADMIN_ENABLED = os.getenv('ADMIN_ENABLED', 'false').lower() == 'true'
ADMIN_PATH = make_url_path(os.getenv('ADMIN_PATH', 'admin'))

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
    'corsheaders',
    'django_extensions',
    'django_filters',
    'datapunt_api',
    'drf_yasg',
    'rest_framework',
    'rest_framework_gis',
    'leaflet',
]

DEBUG_APPS = ()

# Apps specific for this project go here.
LOCAL_APPS = ['main', 'iot', 'health']

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'opencensus.ext.django.middleware.OpencensusMiddleware',
]

DEBUG_MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'pyinstrument.middleware.ProfilerMiddleware',
]

if DEBUG:
    INSTALLED_APPS += DEBUG_APPS
    MIDDLEWARE += DEBUG_MIDDLEWARE
    CORS_ORIGIN_ALLOW_ALL = True
    # DEBUG_TOOLBAR_PANELS = [
    #     'debug_toolbar.panels.versions.VersionsPanel',
    #     'debug_toolbar.panels.timer.TimerPanel',
    #     'debug_toolbar.panels.settings.SettingsPanel',
    #     'debug_toolbar.panels.headers.HeadersPanel',
    #     'debug_toolbar.panels.request.RequestPanel',
    #     'debug_toolbar.panels.sql.SQLPanel',
    #     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    #     'debug_toolbar.panels.templates.TemplatesPanel',
    #     'debug_toolbar.panels.cache.CachePanel',
    #     'debug_toolbar.panels.logging.LoggingPanel',
    #     'debug_toolbar.panels.redirects.RedirectsPanel',
    #     'debug_toolbar.panels.profiling.ProfilingPanel',
    # ]

AUTHENTICATION_BACKENDS = [
    'iot.auth.OIDCAuthenticationBackend',
]

SENSOR_REGISTER_ADMIN_ROLE_NAME = os.getenv('SENSOR_REGISTER_ADMIN_ROLE_NAME', 'x')

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

DATABASE_HOST = os.getenv("DATABASE_HOST", "database")
DATABASE_NAME = os.getenv("DATABASE_NAME", "dev")
DATABASE_USER = os.getenv("DATABASE_USER", "dev")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "dev")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_OPTIONS = {'sslmode': 'allow', 'connect_timeout': 5}

if 'azure.com' in DATABASE_HOST:
    DATABASE_PASSWORD = azure.auth.db_password
    DATABASE_OPTIONS['sslmode'] = 'require'

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "CONN_MAX_AGE": 60 * 5,
        "PORT": DATABASE_PORT,
        'OPTIONS': {'sslmode': 'allow', 'connect_timeout': 5},
    },
}

# Internationalization
LANGUAGE_CODE = 'nl-NL'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Network related
# USE_X_FORWARDED_HOST = True
BASE_URL = os.getenv('BASE_URL', '')
FORCE_SCRIPT_NAME = BASE_URL


# Static files (CSS, JavaScript, Images) and media files
STATIC_URL = urljoin(f'{BASE_URL}/', 'static/')
STATIC_ROOT = '/static/'

MEDIA_URL = urljoin(f'{BASE_URL}/', 'media/')
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'media')


# Django cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Django Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'formatters': {
        'console': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'},
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        'iot': {
            'level': 'INFO',
            'propagate': True,
        },
        'opencensus': {
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'level': os.getenv(
                'DJANGO_LOG_LEVEL', 'ERROR' if 'pytest' in sys.argv[0] else 'INFO'
            ).upper(),
            'propagate': True,
        },
    },
}

APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv(
    'APPLICATIONINSIGHTS_CONNECTION_STRING'
)

if APPLICATIONINSIGHTS_CONNECTION_STRING:
    OPENCENSUS = {
        'TRACE': {
            'SAMPLER': 'opencensus.trace.samplers.ProbabilitySampler(rate=1)',
            'EXPORTER': f"opencensus.ext.azure.trace_exporter.AzureExporter(connection_string='{APPLICATIONINSIGHTS_CONNECTION_STRING}')",
        }
    }
    LOGGING['handlers']['azure'] = {
        'level': "DEBUG",
        'class': "opencensus.ext.azure.log_exporter.AzureLogHandler",
        'connection_string': APPLICATIONINSIGHTS_CONNECTION_STRING,
    }
    LOGGING['loggers']['django']['handlers'] = ['azure', 'console']
    LOGGING['loggers']['iot']['handlers'] = ['azure', 'console']

# Django REST framework settings
REST_FRAMEWORK = dict(
    PAGE_SIZE=100,
    MAX_PAGINATE_BY=100,
    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    DEFAULT_AUTHENTICATION_CLASSES=(
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

## OpenId Connect settings ##
LOGIN_URL = 'oidc_authentication_init'
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/api/"
LOGIN_REDIRECT_URL_FAILURE = '/static/403.html'

OIDC_BASE_URL = os.getenv('OIDC_BASE_URL')
OIDC_RP_CLIENT_ID = os.getenv('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET')
OIDC_OP_AUTHORIZATION_ENDPOINT = f'{OIDC_BASE_URL}/oauth2/v2.0/authorize'
OIDC_OP_TOKEN_ENDPOINT = f'{OIDC_BASE_URL}/oauth2/v2.0/token'
OIDC_OP_USER_ENDPOINT = 'https://graph.microsoft.com/oidc/userinfo'
OIDC_OP_JWKS_ENDPOINT = f'{OIDC_BASE_URL}/discovery/v2.0/keys'
OIDC_OP_LOGOUT_ENDPOINT = f'{OIDC_BASE_URL}/oauth2/v2.0/logout'
OIDC_RP_SIGN_ALGO = 'RS256'

# Only enabled the plugin if admin is enabled
if ADMIN_ENABLED:
    THIRD_PARTY_APPS += ('mozilla_django_oidc',)
    MIDDLEWARE += ('mozilla_django_oidc.middleware.SessionRefresh',)
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += (
        'mozilla_django_oidc.contrib.drf.OIDCAuthentication',
    )

# Sentry logging
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=os.getenv('ENVIRONMENT', 'dev'),
        release=os.getenv('VERSION', 'dev'),
        integrations=[
            DjangoIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
