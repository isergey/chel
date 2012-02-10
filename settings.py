# encoding: utf-8
import os
import sys
from local_settings import *


sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))
sys.path.insert(0, os.path.join(PROJECT_PATH, "vendors"))


ADMINS = (
# ('Your Name', 'your_email@example.com'),
)


MANAGERS = ADMINS



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'

gettext = lambda s: s
LANGUAGES = (
    ('ru', gettext('Russian')),
    ('en', gettext('English')),
    #('tt', gettext('Tatar')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True



# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''



# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)



# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
#    )),
    #     'django.template.loaders.eggs.Loader',
)


#TEMPLATE_LOADERS = (
#        ('django.template.loaders.cached.Loader', (
#    'django.template.loaders.filesystem.Loader',
#    'django.template.loaders.app_directories.Loader',
#        )),
#         'django.template.loaders.eggs.Loader',
#    )



TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    #'django.contrib.messages.context_processors.messages',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'libcms.urls'

INSTALLED_APPS = (


    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # 'django.contrib.admindocs',

    # vendor apps
    'mptt',
    'guardian',
    'debug_toolbar',

    # cms apps
    'core',
    'users',
    'ask_librarian',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/mylog.log',
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
            },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django_request.log',
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
            },
        },
    'loggers': {

        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {# Stop SQL debug from logging to main logger
                           'handlers': ['request_handler'],
                           'level': 'DEBUG',
                           'propagate': False
        },
    }
}
# префикс для системы кеширования
KEY_PREFIX = 'libcms'

# guardian settings
ANONYMOUS_USER_ID = -1

