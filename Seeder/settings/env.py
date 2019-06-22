from .base import *

# Enviromental based configuration.

print('Loading ./settings/env.py')

SECRET_KEY = os.environ.get('SECRET_KEY', 'sdfvsdfvsdfvsdfv')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False')
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

THUMBNAIL_DEBUG = os.environ.get('THUMBNAIL_DEBUG', 'False')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split(' ')

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

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'elasticstack.backends.ConfigurableElasticSearchEngine',
        'URL': 'http://elastic:9200/',
        'INDEX_NAME': 'haystack',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': os.environ.get('MEMCACHED', 'memcached:11211'),
    }
}

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'False')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webarchiv@nkp.cz')
SERVER_EMAIL= os.environ.get('SERVER_EMAIL', 'webarchiv@nkp.cz')

MANET_URL = os.environ.get('MANET', 'http://manet:8891/')
WAKAT_URL = os.environ.get('WAKAT_URL', 'http://kat.webarchiv.cz/?url_id={id}')
WAYBACK_URL = os.environ.get('WAYBACK_URL', 'https://wayback.webarchiv.cz/wayback/*/{url}')
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN'),
}
