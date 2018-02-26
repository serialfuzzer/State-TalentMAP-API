"""
Django settings for talentmap_api project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import dj_database_url
import datetime

import saml2
import saml2.saml

# This supports swagger https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Simple function to evaluate if an environment variable is truthy
def bool_env_variable(name):
    return os.environ.get(name) in ["1", "True", "true", True]


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool_env_variable("DJANGO_DEBUG")

# Whether to enable saml2 endpoints
ENABLE_SAML2 = bool_env_variable("ENABLE_SAML2")

# This is * for now, but should be set to a proper host when deployed
ALLOWED_HOSTS = ['*']

# CORS Settings
CORS_ORIGIN_ALLOW_ALL = True

# Login paths
LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

# Check for SAML2 enable
if ENABLE_SAML2:
    LOGIN_URL = '/saml2/login/'
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
    'django.contrib.postgres',

    # Third-party
    'corsheaders',
    'django_filters',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_expiring_authtoken',
    'rest_framework_swagger',
    'debug_toolbar',
    'djangosaml2',
    'simple_history',

    # TalentMap Apps
    'talentmap_api.common',
    'talentmap_api.position',
    'talentmap_api.language',
    'talentmap_api.organization',
    'talentmap_api.messaging',
    'talentmap_api.user_profile',
    'talentmap_api.bidding',
    'talentmap_api.permission',
    'talentmap_api.glossary',
    'talentmap_api.integrations'
]

MIDDLEWARE = [
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

# SAML Settings
SAML_CONFIG = {}

# Lookup by email
SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'
# Use their uid as their username
SAML_USE_NAME_ID_AS_USERNAME = True
# Create a new Django user if we have a saml2 user we don't know
SAML_CREATE_UNKNOWN_USER = True

if ENABLE_SAML2:
    # See https://github.com/knaperek/djangosaml2 for more information
    SAML_ATTRIBUTE_MAPPING = {
        'nameidentifier': ('username', ),
        'EmailAddress': ('email', ),
        'givenname': ('first_name', ),
        'surname': ('last_name', ),
    }

    SAML_CONFIG = {
        "strict": False,
        "allow_unsolicited": True,

        # full path to the xmlsec1 binary program
        'xmlsec_binary': os.environ.get('SAML2_XMLSEC1_PATH'),

        # your entity id, usually your subdomain plus the url to the metadata view
        'entityid': f"{os.environ.get('SAML2_NETWORK_LOCATION')}saml2/metadata/",

        # directory with attribute mapping
        'attribute_map_dir': os.path.join(BASE_DIR, 'talentmap_api', 'saml2', 'attribute_maps'),

        # this block states what services we provide
        'service': {
            # We are a service provider
            'sp': {
                'name': 'TalentMAP',
                'name_id_format': saml2.saml.NAMEID_FORMAT_PERSISTENT,
                'endpoints': {
                    # url and binding to the assetion consumer service view
                    # do not change the binding or service name
                    'assertion_consumer_service': [
                        (f"{os.environ.get('SAML2_NETWORK_LOCATION')}saml2/acs/",
                            saml2.BINDING_HTTP_POST),
                    ],
                    # url and binding to the single logout service view
                    # do not change the binding or service name
                    'single_logout_service': [
                        (f"{os.environ.get('SAML2_NETWORK_LOCATION')}saml2/ls/",
                            saml2.BINDING_HTTP_REDIRECT),
                        (f"{os.environ.get('SAML2_NETWORK_LOCATION')}ls/post",
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
                    os.environ.get('SAML2_IDP_METADATA_ENDPOINT'): {
                        'single_sign_on_service': {
                            saml2.BINDING_HTTP_REDIRECT: os.environ.get('SAML2_IDP_SSO_LOGIN_ENDPOINT'),
                        },
                        'single_logout_service': {
                            saml2.BINDING_HTTP_REDIRECT: os.environ.get('SAML2_IDP_SLO_LOGOUT_ENDPOINT'),
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
        'debug': os.environ.get('SAML2_DEBUG'),

        # Signing
        'key_file': os.environ.get('SAML2_SIGNING_KEY'),  # private part
        'cert_file': os.environ.get('SAML2_SIGNING_CERT'),  # public part

        # Encryption
        'encryption_keypairs': [{
            'key_file': os.environ.get('SAML2_ENCRYPTION_KEY'),  # private part
            'cert_file': os.environ.get('SAML2_ENCRYPTION_CERT'),  # public part
        }],

        # Our metadata
        'contact_person': [
            {
                'given_name': os.environ.get('SAML2_TECHNICAL_POC_FIRST_NAME'),
                'sur_name': os.environ.get('SAML2_TECHNICAL_POC_LAST_NAME'),
                'company': os.environ.get('SAML2_TECHNICAL_POC_COMPANY'),
                'email_address': os.environ.get('SAML2_TECHNICAL_POC_EMAIL'),
                'contact_type': 'technical'
            },
            {
                'given_name': os.environ.get('SAML2_ADMINISTRATIVE_POC_FIRST_NAME'),
                'sur_name': os.environ.get('SAML2_ADMINISTRATIVE_POC_LAST_NAME'),
                'company': os.environ.get('SAML2_ADMINISTRATIVE_POC_COMPANY'),
                'email_address': os.environ.get('SAML2_ADMINISTRATIVE_POC_EMAIL'),
                'contact_type': 'administrative'
            },
        ],

        "valid_for": 24  # Our metadata is valid for 24-hours
    }  # End SAML config

# Logging Settings
debug_log_destination = os.environ.get('DEBUG_LOG_DESTINATION', 'console')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': [debug_log_destination],
            'level': 'DEBUG',
            'propagate': True,
        },
        'console': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'synchronization': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'zeep.transports': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
            'filters': ['require_debug_true']
        },
    }
}

# Add our destination log file for debugging if we're logging to file
if debug_log_destination == 'file':
    LOGGING['handlers']['file'] = {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filters': ['require_debug_true'],
        'filename': os.path.join(BASE_DIR, 'logs/debug.log'),
        'formatter': 'verbose'
    }


WSGI_APPLICATION = 'talentmap_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# Set up the DB from a connection string in the environment variable, DATABASE_URL
# see https://github.com/kennethreitz/dj-database-url for more info

DATABASES = {'default': dj_database_url.config(conn_max_age=1)}


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
