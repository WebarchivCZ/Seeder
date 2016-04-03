from base import *


SECRET_KEY = ''
assert SECRET_KEY, 'You must set secret key!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['example.com', 'www.example.com']

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
# since we use special PostgresSQL fields we cannot simply use any db.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<db name>',
        'USER': '<db user>',
        'PASSWORD': '<db pass>'
    },
    'legacy_seeder': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '???',
        'USER': '???',
        'PASSWORD': '???'
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://haystack:9200/',
        'INDEX_NAME': 'haystack',
    },
}


RAVEN_CONFIG = {
    'dsn': 'https://<key>:<secret>@app.getsentry.com/<project>',
}