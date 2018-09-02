"""
Django settings for cmwc project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$+(218y1qhycniwjae6n(6pib=^9&dg%l_s9arj=1ltj*5gx+n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

TEMPLATE_DIRS = ('templates/',)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

DEFAULT_FROM_EMAIL = 'do-not-reply@naccc2018.com'

AUTH_USER_MODEL = 'nacccusers.NACCCUser'

# Honor the "X-Forwarded-Proto" header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Allow all host headers
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'south',
    'paypal.standard',
    'paypal.standard.ipn',
    'paypal.standard.pdt',
    'nacccusers',
    'racers',
    'races',
    'raceentries',
    'checkpoints',
    'jobs',
    'runs',
    'home',
    'widget_tweaks',
    'racecontrol',
    'rest_framework',
    'storages',
    'streamer',
    'results',
    'provider',
    'provider.oauth2',
    'authorizedcheckpoints',
    'mobilecheckpoint',
    'racelogs',
    'dispatch',
)

PAYPAL_IDENTITY_TOKEN = "Orx5c4XVqv8VqZizQdUdJ3hQshLik2MuIRtF_boHKhZidzW262C-h1SkLVa"
PAYPAL_TEST = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
    'standard': {
        'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
        'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'paypal.standard.ipn': {
            'handlers': ['console'],
            'level': 'DEBUG'
       },
   }
}

import raven

RAVEN_CONFIG = {
    'dsn': 'https://7ef81bb8c17a49be992f6cdebbd99d75:f5a2be74c21940c48c71ea143870f0f0@sentry.io/1231476',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    #'release': raven.fetch_git_sha(os.path.abspath(os.pardir)),
}


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CONTEXT_PROCESSORS = (
    'django.core.context_processors.csrf',
)

ROOT_URLCONF = 'naccc.urls'

WSGI_APPLICATION = 'naccc.wsgi.application'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/staticfiles/"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@mg.naccc2018.com'
EMAIL_HOST_PASSWORD = 'a147716148f5d037e7d25169a3ea6f6c-115fe3a6-0d9fcd82'
EMAIL_USE_TLS = True

MAILCHIMP_USERNAME = 'naccc2018'
MAILCHIMP_API_KEY = '73e4693f5ed7ff2cd92e3b35a5abf0f1-us16'

USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

SERVE_RACER_PHOTOS_FROM_S3 = False

PAYPAL_RECEIVER_EMAIL = "philabma@gmail.com"

REGISTRATION_PRICE = "80.00"
VOLUNTEER_PRICE = "20.00"
LOGIN_REDIRECT_URL = "admin"

try:
    from .local_settings import *
except:
    pass
    
