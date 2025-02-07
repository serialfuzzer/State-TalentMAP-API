"""
Django settings for talentmap_api project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import datetime
import dj_database_url

import saml2
import saml2.saml
import pydash

from saml2.config import SPConfig
from django.apps import AppConfig



# For upgrade to django 3.x
AppConfig.default = False
DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# This supports swagger https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


def get_delineated_environment_variable(variable, default=None):
    '''
    Returns an environment variable, using the DJANGO_ENVIRONMENT_NAME variable
    as a prefix.
    '''
    env_name = os.environ.get('DJANGO_ENVIRONMENT_NAME', '')
    val = os.environ.get(f'{env_name}{variable}', None)
    if val is None:
        # Try with no env_name (this can be an issue when using runserver)
        val = os.environ.get(f'{variable}', None)
    if val is None:
        val = default
    return val


# Simple function to evaluate if an environment variable is truthy
def bool_env_variable(name):
    return get_delineated_environment_variable(name) in ["1", "True", "true", True]


# SMTP email settings
EMAIL_ENABLED = bool_env_variable("EMAIL_ENABLED")
EMAIL_HOST = get_delineated_environment_variable("EMAIL_HOST")
EMAIL_PORT = get_delineated_environment_variable("EMAIL_PORT")
EMAIL_HOST_USER = get_delineated_environment_variable("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_delineated_environment_variable("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = bool_env_variable("EMAIL_USE_TLS")
EMAIL_FROM_ADDRESS = get_delineated_environment_variable("EMAIL_FROM_ADDRESS")
EMAIL_IS_DEV = bool_env_variable("EMAIL_IS_DEV")
EMAIL_DEV_TO = get_delineated_environment_variable("EMAIL_DEV_TO")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_delineated_environment_variable("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool_env_variable("DJANGO_DEBUG")

# Whether to enable saml2 endpoints
ENABLE_SAML2 = bool_env_variable("ENABLE_SAML2")

# This is * for now, but should be set to a proper host when deployed
ALLOWED_HOSTS = ['*']

# CORS Settings
CORS_ORIGIN_ALLOW_ALL = True

# Check for SAML2 enable
if ENABLE_SAML2:
    # We want to use Django login for Swagger all the time, so we comment this out
    # LOGIN_URL = '/saml2/login/'
    SESSION_EXPIRE_AT_BROWSER_CLOSE = bool_env_variable('SAML2_SESSION_EXPIRE_AT_BROWSER_CLOSE')

# Authorization token lifetime
EXPIRING_TOKEN_LIFESPAN = datetime.timedelta(days=1)

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

if ENABLE_SAML2:
    AUTHENTICATION_BACKENDS += ('djangosaml2.backends.Saml2Backend',)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',
    'django_filters',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_expiring_authtoken',
    'rest_framework_filters',
    'drf_yasg',
    'debug_toolbar',
    'djangosaml2',
    'simple_history',
    "sslserver",

    # TalentMap Apps
    'talentmap_api.common',
    'talentmap_api.position',
    'talentmap_api.organization',
    'talentmap_api.messaging',
    'talentmap_api.user_profile',
    'talentmap_api.bidding',
    'talentmap_api.permission',
    'talentmap_api.glossary',
    'talentmap_api.projected_vacancies',
    'talentmap_api.available_positions',
    'talentmap_api.projected_tandem',
    'talentmap_api.available_tandem',
    'talentmap_api.log_viewer',
    'talentmap_api.administration',
    'talentmap_api.feature_flags',
    'talentmap_api.stats',
    'talentmap_api.fsbid',
    'talentmap_api.cdo',

    # Health Check
    'health_check',                             # required
    'health_check.db',                          # stock Django health checkers
    'health_check.storage',
    'health_check.contrib.migrations',
    'health_check.contrib.psutil',              # disk and memory utilization; requires psutil
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Third-party
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',

    # Our middleware
    'talentmap_api.common.middleware.IE11Middleware',
    'talentmap_api.common.middleware.ExposeHeadersMiddleware',
]

ROOT_URLCONF = 'talentmap_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'talentmap_api.common.pagination.ControllablePageNumberPagination',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'talentmap_api.common.renderers.BrowsableAPIRendererWithoutForms',
        'talentmap_api.common.renderers.PaginatedCSVRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'talentmap_api.common.filters.DisabledHTMLFilterBackend',
        'talentmap_api.common.filters.RelatedOrderingFilter'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_expiring_authtoken.authentication.ExpiringTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_USE_CACHE': 'default',
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 86400,  # 1 day
    'DEFAULT_CACHE_KEY_FUNC': 'talentmap_api.common.cache.key_constructor.key_func'
}

# SAML Settings
SAML_CONFIG = {}

# Lookup by email
SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'
# Use their uid as their username
SAML_USE_NAME_ID_AS_USERNAME = True
# Create a new Django user if we have a saml2 user we don't know
SAML_CREATE_UNKNOWN_USER = True

if ENABLE_SAML2:
    LOGIN_REDIRECT_URL = get_delineated_environment_variable('SAML_LOGIN_REDIRECT_URL')

    # See https://github.com/knaperek/djangosaml2 for more information
    SAML_ATTRIBUTE_MAPPING = {
        'EmailAddress': ('email', 'username', ),
        'givenname': ('first_name', ),
        'surname': ('last_name', ),
    }

    def config_settings_loader(request):
        isPublic = False
        acs = f"{get_delineated_environment_variable('FRONT_END_ACS_BINDING')}"
        if request.GET.get('public') is not None:
            isPublic = True
            acs = f"{get_delineated_environment_variable('FRONT_END_ACS_BINDING')}"
        if isPublic is True:
            acs = f"{get_delineated_environment_variable('FRONT_END_ACS_BINDING_PUBLIC')}"
        conf = SPConfig()

        conf.load({
            "strict": False,

            # full path to the xmlsec1 binary program
            'xmlsec_binary': get_delineated_environment_variable('SAML2_XMLSEC1_PATH'),

            # acceptable time differential, in seconds
            'accepted_time_diff': 60,

            # your entity id, usually your subdomain plus the url to the metadata view
            'entityid': f"{get_delineated_environment_variable('SAML2_NETWORK_LOCATION')}saml2/metadata/",

            # directory with attribute mapping
            'attribute_map_dir': os.path.join(BASE_DIR, 'talentmap_api', 'saml2', 'attribute_maps'),

            # this block states what services we provide
            'service': {
                # We are a service provider
                'sp': {
                    'name': 'TalentMAP',
                    'allow_unsolicited': True,
                    'name_id_format': saml2.saml.NAMEID_FORMAT_PERSISTENT,
                    'want_response_signed': False,
                    'endpoints': {
                        # url and binding to the assetion consumer service view
                        # do not change the binding or service name
                        'assertion_consumer_service': [
                            (f"{get_delineated_environment_variable('FRONT_END_ACS_BINDING')}",
                             saml2.BINDING_HTTP_POST),
                        ],
                        # url and binding to the single logout service view
                        # do not change the binding or service name
                        'single_logout_service': [
                            (f"{get_delineated_environment_variable('SAML2_NETWORK_LOCATION')}saml2/ls/",
                             saml2.BINDING_HTTP_REDIRECT),
                            (f"{get_delineated_environment_variable('SAML2_NETWORK_LOCATION')}ls/post",
                             saml2.BINDING_HTTP_POST),
                        ],
                    },

                    # attributes that this project need to identify a user
                    'required_attributes': ['EmailAddress', 'nameidentifier', 'givenname', 'surname'],

                    # attributes that may be useful to have but not required
                    # TODO: What attributes are we getting back from DOS IdP?
                    'optional_attributes': [],

                    # in this section the list of IdPs we talk to are defined
                    'idp': {
                        # the keys of this dictionary are entity ids
                        get_delineated_environment_variable('SAML2_IDP_METADATA_ENDPOINT'): {
                            'single_sign_on_service': {
                                saml2.BINDING_HTTP_REDIRECT: get_delineated_environment_variable('SAML2_IDP_SSO_LOGIN_ENDPOINT'),
                            },
                            'single_logout_service': {
                                saml2.BINDING_HTTP_REDIRECT: get_delineated_environment_variable('SAML2_IDP_SLO_LOGOUT_ENDPOINT'),
                            },
                        },
                    },  # End IDP config
                },  # End SP config
            },  # End Service config

            # where the remote metadata is stored
            'metadata': {
                'local': [os.path.join(BASE_DIR, 'talentmap_api', 'saml2', 'remote_metadata', 'remote_metadata.xml')],
            },

            # set to 1 to output debugging information
            'debug': get_delineated_environment_variable('SAML2_DEBUG'),

            # Signing
            'key_file': get_delineated_environment_variable('SAML2_SIGNING_KEY'),  # private part
            'cert_file': get_delineated_environment_variable('SAML2_SIGNING_CERT'),  # public part

            # Encryption
            'encryption_keypairs': [{
                'key_file': get_delineated_environment_variable('SAML2_ENCRYPTION_KEY'),  # private part
                'cert_file': get_delineated_environment_variable('SAML2_ENCRYPTION_CERT'),  # public part
            }],

            # Our metadata
            'contact_person': [
                {
                    'given_name': get_delineated_environment_variable('SAML2_TECHNICAL_POC_FIRST_NAME'),
                    'sur_name': get_delineated_environment_variable('SAML2_TECHNICAL_POC_LAST_NAME'),
                    'company': get_delineated_environment_variable('SAML2_TECHNICAL_POC_COMPANY'),
                    'email_address': get_delineated_environment_variable('SAML2_TECHNICAL_POC_EMAIL'),
                    'contact_type': 'technical'
                },
                {
                    'given_name': get_delineated_environment_variable('SAML2_ADMINISTRATIVE_POC_FIRST_NAME'),
                    'sur_name': get_delineated_environment_variable('SAML2_ADMINISTRATIVE_POC_LAST_NAME'),
                    'company': get_delineated_environment_variable('SAML2_ADMINISTRATIVE_POC_COMPANY'),
                    'email_address': get_delineated_environment_variable('SAML2_ADMINISTRATIVE_POC_EMAIL'),
                    'contact_type': 'administrative'
                },
            ],

            "valid_for": 24  # Our metadata is valid for 24-hours
        })  # End SAML config
        return conf


def skip_lb_requests(record):
    record = pydash.get(record, 'args[0]')
    if isinstance(record, str) and record.startswith('HEAD / HTTP'):
        return False
    return True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'skip_lb_requests': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_lb_requests
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['skip_lb_requests'],
        },
        'auth': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': get_delineated_environment_variable('DJANGO_LOG_DIRECTORY', '/var/log/talentmap/') + get_delineated_environment_variable('DJANGO_LOG_AUTH_NAME', 'auth.log'),
            'formatter': 'simple',
        },
        'access': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': get_delineated_environment_variable('DJANGO_LOG_DIRECTORY', '/var/log/talentmap/') + get_delineated_environment_variable('DJANGO_LOG_ACCESS_NAME', 'access.log'),
            'formatter': 'simple',
        },
        'permission': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': get_delineated_environment_variable('DJANGO_LOG_DIRECTORY', '/var/log/talentmap/') + get_delineated_environment_variable('DJANGO_LOG_PERM_NAME', 'permissions.log'),
            'formatter': 'simple',
        },
        'db': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': get_delineated_environment_variable('DJANGO_LOG_DIRECTORY', '/var/log/talentmap/') + get_delineated_environment_variable('DJANGO_LOG_DB_NAME', 'db.log'),
            'formatter': 'simple',
        },
        'sync': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': get_delineated_environment_variable('DJANGO_LOG_DIRECTORY', '/var/log/talentmap/') + get_delineated_environment_variable('DJANGO_LOG_SYNC_NAME', 'sync.log'),
            'formatter': 'simple',
        },
        'generic': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': get_delineated_environment_variable('DJANGO_LOG_DIRECTORY', '/var/log/talentmap/') + get_delineated_environment_variable('DJANGO_LOG_GENERIC_NAME', 'talentmap.log'),
            'formatter': 'simple',
        },
    },
    'loggers': {
        'console': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'access'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console', 'db'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'talentmap_api': {
            'handlers': ['console', 'generic'],
            'level': 'INFO',
            'propagate': False,
        },
        'talentmap_api.permission': {
            'handlers': ['console', 'permission'],
            'level': 'INFO',
            'propagate': False,  # Consume these logs
        },
        'talentmap_api.saml2': {
            'handlers': ['console', 'auth'],
            'level': 'DEBUG',
            'propagate': False,  # Consume these logs
        },
        'zeep.transports': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
            'filters': ['require_debug_true']
        },
    }
}

WSGI_APPLICATION = 'talentmap_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# Set up the DB from a connection string in the environment variable, DATABASE_URL
# see https://github.com/kennethreitz/dj-database-url for more info

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': get_delineated_environment_variable("DATABASE_URL"),
        'USER': get_delineated_environment_variable("DATABASE_USER"),
        'PASSWORD': get_delineated_environment_variable("DATABASE_PW"),
        # 'CONN_MAX_AGE': 300,
        # 'OPTIONS': {'threaded': True}
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Debug toolbar settings
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'talentmap_api/static/')

WS_ROOT_API_URL = get_delineated_environment_variable('WS_ROOT_API_URL', 'http://mock_fsbid:3333')
SECREF_URL = get_delineated_environment_variable('SECREF_URL', 'http://mock_fsbid:3333/v2/SECREF')
EMPLOYEES_API_URL = get_delineated_environment_variable('EMPLOYEES_API_URL', 'http://mock_fsbid:3333/v1/Employees')
CP_API_URL = get_delineated_environment_variable('CP_API_URL', 'http://mock_fsbid:3333/v1/cyclePositions')
CP_API_V2_URL = get_delineated_environment_variable('CP_API_V2_URL', 'http://mock_fsbid:3333/v2/cyclePositions')
ORG_API_URL = get_delineated_environment_variable('ORG_API_URL', 'http://mock_fsbid:3333/v1/Organizations')
CLIENTS_API_URL = get_delineated_environment_variable('CLIENTS_API_URL', 'http://mock_fsbid:3333/v1/Clients')
CLIENTS_API_V2_URL = get_delineated_environment_variable('CLIENTS_API_V2_URL', 'http://mock_fsbid:3333/v2/clients')
PV_API_V2_URL = get_delineated_environment_variable('PV_API_V2_URL', 'http://mock_fsbid:3333/v2/futureVacancies')
HRDATA_URL = get_delineated_environment_variable('HRDATA_URL', 'http://mock_fsbid:3333/HR')
HRDATA_URL_EXTERNAL = get_delineated_environment_variable('HRDATA_URL_EXTERNAL', 'http://mock_fsbid:3333/HR')
AVATAR_URL = get_delineated_environment_variable('AVATAR_URL', 'https://usdos.sharepoint.com/_layouts/15/userphoto.aspx')
TP_API_URL = get_delineated_environment_variable('TP_API_URL', 'http://mock_fsbid:3333/v1/TrackingPrograms')
AGENDA_API_URL = get_delineated_environment_variable('AGENDA_API_URL', 'http://mock_fsbid:3333/v1/Agendas')
PANEL_API_URL = get_delineated_environment_variable('PANEL_API_URL', 'http://mock_fsbid:3333/v1/panels')
PERSON_API_URL = get_delineated_environment_variable('PERSON_API_URL', 'http://mock_fsbid:3333/v3/persons')
BIDS_API_V2_URL = get_delineated_environment_variable('BIDS_API_V2_URL', 'http://mock_fsbid:3333/v2/bids')
POSITIONS_API_URL = get_delineated_environment_variable('POSITIONS_API_URL', 'http://mock_fsbid:3333/v1/positions')
POSITIONS_API_V2_URL = get_delineated_environment_variable('POSITIONS_API_V2_URL', 'http://mock_fsbid:3333/v2/positions')
PUBLISHABLE_POSITIONS_API_URL = get_delineated_environment_variable('PUBLISHABLE_POSITIONS_API_URL', 'http://mock_fsbid:3333/v1/publishablePositions')
SAML_CONFIG_LOADER = 'talentmap_api.settings.config_settings_loader'

# remove actual values before committing
AD_ID = 'DOMAIN\\USERNAME'
OBC_URL = get_delineated_environment_variable('OBC_URL', 'http://localhost:4000')
OBC_URL_EXTERNAL = get_delineated_environment_variable('OBC_URL_EXTERNAL', 'http://localhost:4000/external')

# SSL cert
HRONLINE_CERT = get_delineated_environment_variable('HRONLINE_CERT', None)

# defaults from https://pypi.org/project/django-cors-headers/ plus our custom headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'jwt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        "api_key": {
            "type": "apiKey",
            "name": "JWT",
            "in": "header",
            "description": "JWT authorization"
        },
    },
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
}

FAVORITES_LIMIT = 50
