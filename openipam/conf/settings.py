from __future__ import unicode_literals
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages import constants as message_constants
import hashlib
import socket
import datetime


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DEBUG_MONITOR = True if DEBUG else False
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
try:
    from local_settings import *
except:
    pass

DATABASES = locals().pop('DATABASES', {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%s/development.db' % BASE_DIR,  # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
})


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Denver'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '%s/media/' % BASE_DIR

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '%s/static/' % BASE_DIR

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
# STATICFILES_DIRS = (
#     # Put strings here, like "/home/html/static" or "C:/www/django/static".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
# )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)

FIXTURE_DIRS = (
   '%s/fixtures/' % BASE_DIR,
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = locals().pop(
    'LOCAL_SECRET_KEY',
    hashlib.md5((socket.gethostname() + ')*)&8a36)6f-ne5(-!8a(vvfse4bsI&*#^@$^(eyg&@0=7=y@').encode('ascii')).hexdigest()
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

LOCAL_MIDDLEWARE_CLASSES = locals().pop('LOCAL_MIDDLEWARE_CLASSES', ())
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'openipam.middleware.LoginRequiredMiddleware',
    'openipam.middleware.MimicUserMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

) + LOCAL_MIDDLEWARE_CLASSES

ROOT_URLCONF = 'openipam.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'openipam.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

LOCAL_INSTALLED_APPS = locals().pop('LOCAL_INSTALLED_APPS', ())
INSTALLED_APPS = (
    # openIPAM Apps
    'openipam.core',
    'openipam.user',
    'openipam.api',
    'openipam.hosts',
    'openipam.network',
    'openipam.dns',
    'openipam.log',

    # Admin Tools
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    'djangobower',
    'django_extensions',
    'widget_tweaks',
    'crispy_forms',
    'autocomplete_light',
    'rest_framework',
    'rest_framework.authtoken',
    'guardian',
    'netfields',

    # Two factor auth
    #'django_otp',
    #'django_otp.plugins.otp_static',
    #'django_otp.plugins.otp_totp',
    #'two_factor',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',


    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

) + LOCAL_INSTALLED_APPS

OPENIPAM = {
    'GUEST_HOSTNAME_FORMAT': ['g-', '.guests.usu.edu'],
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'openipam.core.context_processors.gravatar',
    'openipam.core.context_processors.root_path',
    'openipam.core.context_processors.feature_form',
    'openipam.api.context_processors.api_version',
)

BOWER_COMPONENTS_ROOT = '%s/components/' % BASE_DIR
BOWER_PATH = locals().pop('LOCAL_BOWER_PATH', '/usr/bin/bower')

BOWER_INSTALLED_APPS = (
    'jquery#2.1.1',
    'bootstrap#3.2.0',
    'datatables-bootstrap3',
    'datatables#1.10.2',
    'jquery.cookie#1.4.1',
    'chosen-bower',
    'intro.js#0.9.0',
)

# Hack to find bower components
STATICFILES_DIRS = (
    os.path.join(BOWER_COMPONENTS_ROOT, 'bower_components'),
)

MESSAGE_TAGS = {
    message_constants.DEBUG: 'warning',
    message_constants.ERROR: 'danger',
}

LOCAL_AUTHENTICATION_BACKENDS = locals().pop('LOCAL_AUTHENTICATION_BACKENDS', ())
AUTHENTICATION_BACKENDS = (
    #'django.contrib.auth.backends.ModelBackend',
    'openipam.core.backends.CaseInsensitiveModelBackend',
    'guardian.backends.ObjectPermissionBackend',
) + LOCAL_AUTHENTICATION_BACKENDS

AUTH_USER_MODEL = 'user.User'

ANONYMOUS_USER_ID = -1
LOGIN_EXEMPT_URLS = (
    'password/forgot/',
    'api/?.*',
)
#LOGIN_URL = reverse_lazy('two_factor:login')
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = reverse_lazy('openipam.core.views.index')
LOGOUT_URL = reverse_lazy('django.contrib.auth.views.logout')

REST_FRAMEWORK = {
    'PAGINATE_BY': 25,
    'PAGINATE_BY_PARAM': 'limit',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'openipam.api.permissions.IPAMAPIPermission',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    )
}

JWT_AUTH = {
    'JWT_LEEWAY': 60,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=4)
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

ADMIN_TOOLS_MENU = 'openipam.menu.IPAMMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'openipam.dashboard.IPAMIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'openipam.dashboard.IPAMAppIndexDashboard'

