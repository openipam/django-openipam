# DEBUG = False
# TEMPLATE_DEBUG = False
# DEBUG_SQL = False

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": "",  # Or path to database file if using sqlite3.
        "USER": "",  # Not used with sqlite3.
        "PASSWORD": "",  # Not used with sqlite3.
        "HOST": "",  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",  # Set to empty string for default. Not used with sqlite3.
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 600,
    }
}

# EMAIL_HOST = 'mail.company.com'
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


INTERNAL_IPS = ("127.0.0.1",)

# SESSION_COOKIE_SECURE = True
# SESSION_EXPIRE_BROWSER_CLOSE = True
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_COOKIE_AGE = 28800

# OPENIPAM Settings, see openipam/conf/ipam_settings.py
# OPENIPAM = {
#     'GUEST_HOSTNAME_FORMAT': ['g-', '.guests.company.com'],
#     'DUO_LOGIN': True,
# }

LOCAL_SECRET_KEY = "*sx4u+((&7dl1b^a@87bcdn+pwcms=4hy8+mr^z(1txh(tatv^"


LOCAL_AUTHENTICATION_BACKENDS = (
    # 'django_auth_ldap.backend.LDAPBackend',
    "openipam.core.backends.IPAMLDAPBackend",
)

LOCAL_MIDDLEWARE_CLASSES = [
    # Console SQL
    # 'openipam.core.utils.sql_log.SQLLogToConsoleColorMiddleware',
]

LOCAL_INSTALLED_APPS = (
    # Util Apps
    # 'debug_toolbar',
    # 'debug_toolbar_line_profiler',
    # 'gunicorn',
    # 'devserver',
    # 'djsupervisor',
)

LOCAL_MIDDLEWARE_CLASSES = (
    # Debug Toolbar
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'openipam.core.utils.sql_log.SQLLogToConsoleColorMiddleware',
)

# LOCAL_BOWER_PATH = '/usr/local/bin/bower'

# DEBUG_MIDDLEWARE_CLASS = [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

# DEBUG_TOOLBAR_PATCH_SETTINGS = False

# DEBUG_TOOLBAR_PANELS = [
#     # 'debug_toolbar.panels.profiling.ProfilingPanel'
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
# ]
