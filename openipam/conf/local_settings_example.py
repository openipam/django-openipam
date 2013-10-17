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
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    #'debug_toolbar.panels.signals.SignalDebugPanel',
    #'debug_toolbar.panels.logger.LoggingPanel',
    #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    #'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
    'HIDE_DJANGO_SQL': False,
    'TAG': 'div',
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': True
}
