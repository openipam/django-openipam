from django.core.urlresolvers import reverse_lazy
from django.contrib.messages import constants as message_constants

import hashlib
import socket
import datetime
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
try:
    from .local_settings import *  # noqa: F403,F401
    from .local_settings import OPENIPAM  # noqa: F403,F401
except ImportError:
    pass

SENTRY_DSN = locals().pop("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = locals().pop("SENTRY_ENVIRONMENT", "development")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
        environment=SENTRY_ENVIRONMENT,
        integrations=[
            DjangoIntegration(
                transaction_style="url",
            ),
        ],
    )

DATABASES = locals().pop(
    "DATABASES",
    {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            "NAME": "%s/development.db"
            % BASE_DIR,  # Or path to database file if using sqlite3.
            "USER": "",  # Not used with sqlite3.
            "PASSWORD": "",  # Not used with sqlite3.
            "HOST": "",  # Set to empty string for localhost. Not used with sqlite3.
            "PORT": "",  # Set to empty string for default. Not used with sqlite3.
        }
    },
)

TIME_ZONE = "America/Denver"

LANGUAGE_CODE = "en-us"

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = "%s/media/" % BASE_DIR

MEDIA_URL = "/media/"

STATIC_ROOT = "%s/static/" % BASE_DIR

STATIC_URL = "/static/"

# Fixme: Remove bowser and just use nmp
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Hack to find bower components
    "%s/components/bower_components" % BASE_DIR,
    "%s/components/static_components" % BASE_DIR,
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "djangobower.finders.BowerFinder",
)

FIXTURE_DIRS = ("%s/fixtures/" % BASE_DIR,)

SECRET_KEY = locals().pop(
    "LOCAL_SECRET_KEY",
    hashlib.md5(
        (
            socket.gethostname() + ")*)&8a36)6f-ne5(-!8a(vvfse4bsI&*#^@$^(eyg&@0=7=y@"
        ).encode("ascii")
    ).hexdigest(),
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # Put TEMPLATE_DIRS here...
        ],
        # 'APP_DIRS': True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "openipam.core.context_processors.gravatar",
                "openipam.core.context_processors.root_path",
                "openipam.core.context_processors.feature_form",
                "openipam.api.context_processors.api_version",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
                "admin_tools.template_loaders.Loader",
            ],
        },
    }
]

LOCAL_MIDDLEWARE = locals().pop("LOCAL_MIDDLEWARE", [])
DEBUG_MIDDLEWARE = locals().pop("DEBUG_MIDDLEWARE", [])
MIDDLEWARE = (
    DEBUG_MIDDLEWARE
    + [
        "django.middleware.common.CommonMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "openipam.middleware.LoginRequiredMiddleware",
        "openipam.middleware.DuoAuthRequiredMiddleware",
        "openipam.middleware.MimicUserMiddleware",
        "openipam.middleware.SetRemoteAddrMiddleware",
        # Uncomment the next line for simple clickjacking protection:
        # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    + LOCAL_MIDDLEWARE
)

ROOT_URLCONF = "openipam.urls"

WSGI_APPLICATION = "openipam.wsgi.application"

TEST_RUNNER = "django.test.runner.DiscoverRunner"

LOCAL_INSTALLED_APPS = locals().pop("LOCAL_INSTALLED_APPS", ())
INSTALLED_APPS = (
    # openIPAM Apps
    "openipam.core",
    "openipam.user",
    "openipam.api",
    "openipam.hosts",
    "openipam.network",
    "openipam.dns",
    "openipam.log",
    # openIPAM reports
    "openipam.report",
    # Firewall
    # 'openipam.firewall',
    # Admin Tools
    "admin_tools",
    "admin_tools.theming",
    "admin_tools.menu",
    "admin_tools.dashboard",
    "djangobower",
    "django_nvd3",
    "django_extensions",
    "widget_tweaks",
    "django_filters",
    "crispy_forms",
    "autocomplete_light",
    "rest_framework",
    "rest_framework.authtoken",
    "guardian",
    "netfields",
    "taggit",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # 'django.contrib.sites',
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
) + LOCAL_INSTALLED_APPS

# Fixme:  Remove and use npm
BOWER_COMPONENTS_ROOT = "%s/components/" % BASE_DIR
BOWER_PATH = locals().pop("LOCAL_BOWER_PATH", "/usr/bin/bower")
BOWER_INSTALLED_APPS = (
    "jquery#2.1.4",
    "jquer-ui#1.11.4",
    "bootstrap#3.3.5",
    "datatables#1.10.7",
    "jquery.cookie#1.4.1",
    "chosen",
    "intro.js#0.9.0",
    "qTip#1.0.0",
)

MESSAGE_TAGS = {message_constants.DEBUG: "warning", message_constants.ERROR: "danger"}

LOCAL_AUTHENTICATION_BACKENDS = locals().pop("LOCAL_AUTHENTICATION_BACKENDS", ())
AUTHENTICATION_BACKENDS = (
    # 'django.contrib.auth.backends.ModelBackend',
    "openipam.core.backends.CaseInsensitiveModelBackend",
    # "openipam.core.backends.IPAMCASBackend",
    "guardian.backends.ObjectPermissionBackend",
) + LOCAL_AUTHENTICATION_BACKENDS

AUTH_USER_MODEL = "user.User"

ANONYMOUS_USER_ID = -1
LOGIN_EXEMPT_URLS = (
    "favicon.ico" "static/?.*",
    "password/forgot/",
    "logout/",
    "acs/",
    "api/?.*",
    "reports/?.*",
)
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = reverse_lazy("index")
LOGOUT_URL = reverse_lazy("logout")

REST_FRAMEWORK = {
    "PAGINATE_BY": 25,
    "PAGINATE_BY_PARAM": "limit",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "openipam.api.authentication.IPAMJSONWebTokenAuthentication",
        # "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "openipam.api.permissions.IPAMAPIPermission",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

JWT_AUTH = {"JWT_LEEWAY": 60, "JWT_EXPIRATION_DELTA": datetime.timedelta(hours=4)}

CRISPY_TEMPLATE_PACK = "bootstrap3"

ADMIN_TOOLS_MENU = "openipam.core.menu.IPAMMenu"
ADMIN_TOOLS_INDEX_DASHBOARD = "openipam.core.dashboard.IPAMIndexDashboard"
ADMIN_TOOLS_APP_INDEX_DASHBOARD = "openipam.core.dashboard.IPAMAppIndexDashboard"

HOSTNAME_VALIDATION_REGEX = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
