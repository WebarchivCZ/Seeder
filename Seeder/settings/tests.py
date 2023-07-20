from .base import *

SECRET_KEY = 'test'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
