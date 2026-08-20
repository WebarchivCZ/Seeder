from .base import *
import os
from datetime import timedelta

# Enviromental based configuration.

print('Loading ./settings/env.py')

SECRET_KEY = os.environ.get('SECRET_KEY', 'sdfvsdfvsdfvsdfv')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

THUMBNAIL_DEBUG = os.environ.get('THUMBNAIL_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split(' ')

INTERNAL_IPS = os.environ.get('INTERNAL_IPS', '127.0.0.1').split(' ')

FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get(
    'FILE_UPLOAD_MAX_MEMORY_SIZE', 10485760))  # 10*1024*1024 = 10 MiB

CHUNKED_UPLOAD_MAX_BYTES = int(os.environ.get(
    'CHUNKED_UPLOAD_MAX_BYTES', 524288000))
CHUNKED_UPLOAD_EXPIRATION_DELTA = timedelta(seconds=int(os.environ.get(
    'CHUNKED_UPLOAD_EXPIRATION_DELTA', 21600)))
CHUNKED_UPLOAD_PATH = os.environ.get('CHUNKED_UPLOAD_PATH', 'chunked_uploads')

# POST data limits (for large custom seeds uploads)
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get(
    'DATA_UPLOAD_MAX_MEMORY_SIZE', 10485760))  # 10*1024*1024 = 10 MiB
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.environ.get(
    'DATA_UPLOAD_MAX_NUMBER_FIELDS', 1000))  # Default Django limit
DATA_UPLOAD_MAX_NUMBER_FILES = int(os.environ.get(
    'DATA_UPLOAD_MAX_NUMBER_FILES', 100))  # Default Django limit

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
# since we use special PostgresSQL fields we cannot simply use any db.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASS', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
    }
}

# Only cache in production
if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': os.environ.get('MEMCACHED', 'memcached:11211'),
        }
    }

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'False').lower() == 'true'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webarchiv@nkp.cz')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'webarchiv@nkp.cz')

WAKAT_URL = os.environ.get('WAKAT_URL', 'http://kat.webarchiv.cz/?url_id={id}')
WAYBACK_URL = os.environ.get(
    'WAYBACK_URL', 'https://wayback.webarchiv.cz/wayback/*/{url}')
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

EXTINCT_WEBSITES_URL = os.environ.get(
    "EXTINCT_WEBSITES_URL", 'http://10.3.0.24/api/v2')

RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN'),
}
