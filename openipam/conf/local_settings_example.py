try:
    import psycopg2
except:
    from psycopg2ct import compat
    compat.register()

# Import USU settings (LDAP, etc)
from usu_settings import *

#DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600
    }
}

#EMAIL_HOST = 'mail.usu.edu'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = ('127.0.0.1',)

# SESSION_COOKIE_SECURE = True
# SESSION_EXPIRE_BROWSER_CLOSE = True

LOCAL_SECRET_KEY = '*sx4u+((&7dl1b^a@87bcdn+pwcms=4hy8+mr^z(1txh(tatv^'

LOCAL_MIDDLEWARE_CLASSES = (
    # Debug Toolbar
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'djangopad.middleware.sql_log.SQLLogMiddleware',
)

LOCAL_INSTALLED_APPS = (
    # Util Apps
    #'debug_toolbar',
    #'gunicorn',
    #'devserver',
    #'djsupervisor',
)


DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
)
