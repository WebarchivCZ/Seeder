"""
Django settings for Seeder project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import re

from django.utils.translation import ugettext_lazy as _

# that double dirname is necessary since setting is in folder...
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
    },
    'legacy_seeder': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'legacy_seeder',
        'USER': 'root',
        'PASSWORD': 'legacy'
    }
}

ADMINS = (
    ('Visgean Skeloru', 'visgean@gmail.com')
)

IGNORABLE_404_URLS = (
    re.compile(r'\.(php|cgi)$'),
    re.compile(r'^/phpmyadmin/'),
)


# Application definition
INSTALLED_APPS = (
    'raven.contrib.django.raven_compat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # 'djangobower', # everything is on cdn
    'django_tables2',
    'django_filters',
    'bootstrap3',
    'mptt',
    'formtools',
    'reversion',
    'ckeditor',
    'ckeditor_uploader',
    # 'debug_toolbar',
    'django_crontab',
    'sorl.thumbnail',
    'rest_framework',
    'rest_framework.authtoken',
    'dal',
    'dal_select2',
    'haystack',

    'core',
    'publishers',
    'source',
    'voting',
    'comments',
    'contracts',
    'legacy_db',
    'harvests',
    'blacklists',
    'qa',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.i18n",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
    'core.context_processors.core_processor',
)


MIDDLEWARE_CLASSES = (
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'djangobower.finders.BowerFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# APP_DIRS = True
#
# TEMPLATES = {
#     'BACKEND': 'django.template.backends.django.DjangoTemplates',
#     'DIRS': TEMPLATE_DIRS,
#     'APP_DIRS': True,
#     'OPTIONS': {
#         'context_processors': TEMPLATE_CONTEXT_PROCESSORS
#      }
# }


LANGUAGES = (
    ('cs', _('Czech')),
    ('en', _('English')),
)

CALENDAR_LANGUAGES = {
    'cs': 'cz-CZ',
    'en': 'en-US'
}


LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


BOWER_COMPONENTS_ROOT = BASE_DIR
BOWER_INSTALLED_APPS = ()   # everything is on CDN now


LOGIN_URL = '/auth/login/'
LOGOUT_URL = '/auth/logout/'
LOGIN_REDIRECT_URL = '/'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = 'pillow'


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
        ],
        # 'width': '100%',
    }
}

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'core.utils.show_toolbar',
}

CRON_CLASSES = [
    'source.cron.CreateScreenshots',
    'voting.cron.RevivePostponedRounds',
    'contracts.cron.ExpireContracts',
    'contracts.cron.SendEmails',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
       'rest_framework.permissions.AllowAny'
    ]


WAKAT_URL = 'http://forpsi.kitakitsune.org:8080/?url_id={id}'

SEEDS_EXPORT_DIR = 'seeds'
MANET_URL = '127.0.0.1:8891'


QA_EVERY_N_MONTHS = 24