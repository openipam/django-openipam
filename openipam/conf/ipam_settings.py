from django.conf import settings

# TODO: OPENIPAM settings to go here now.
CONFIG_DEFAULTS = {
    'GUESTS_ENABLED': True,
    'GUEST_USER': 'guest',
    'GUEST_HOSTNAME_FORMAT': ['g-', '.guests.example.com'],
    'GUEST_POOL': 'routable-dynamic',
    'APPS': [app.split('.')[1] for app in filter(lambda x: x.split('.')[0] == 'openipam', settings.INSTALLED_APPS)],
    'CONVERT_OLD_PERMISSIONS': True,
    'USER_GROUP': 'ipam-users',
    'ADMIN_GROUP': 'ipam-admins',
    'API_USER_GROUP': 'ipam-api-users',
    'API_ADMIN_GROUP': 'ipam-api-admins',
}

USER_CONFIG = getattr(settings, 'OPENIPAM', {})
CONFIG = CONFIG_DEFAULTS.copy()
CONFIG.update(USER_CONFIG)
