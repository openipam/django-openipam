from django.conf import settings

# TODO: OPENIPAM settings to go here now.
CONFIG_DEFAULTS = {
    'GUESTS_ENABLED': True,
    'GUEST_USER': 'guest',
    'GUEST_GROUP': 'guests',
    'GUEST_HOSTNAME_FORMAT': ['g-', '.guests.example.com'],
    'GUEST_POOL': 'routable-dynamic',
    'APPS': [app.split('.')[1] for app in filter(lambda x: x.split('.')[0] == 'openipam', settings.INSTALLED_APPS)],
    'CONVERT_OLD_PERMISSIONS': False,
    'USER_GROUP': 'ipam-users',
    'ADMIN_GROUP': 'ipam-admins',
    'API_USER_GROUP': 'ipam-api-users',
    'API_ADMIN_GROUP': 'ipam-api-admins',
    'REPORT_USER_GROUP': 'ipam-reports-users',
    'REPORT_ADMIN_GROUP': 'ipam-reports-admins',
    'DEFAULT_PERMISSIONS': {
        'network': {
            'pool': [1,3]
        },
        'dns': {
            'domain': [10,11,12,13,14,15],
            'dnstype': [16,44,33,12,2,15,13,5,1]
        }
    },
    'EMAIL_ADDRESS': 'openipam@lists.usu.edu',
    'NOTIFICATION_EMAIL_ADDRESS': 'OpenIPAM Notifications <servicedesk@usu.edu>',
    'LEGACY_DOMAIN': 'https://legacy.openipam.usu.edu',
    'DISABLED_HOSTS_WEBSITE': 'https://usu.service-now.com/services/disabled.do',
    'CAS_LOGIN': False,
    'DUO_LOGIN': False,
    'DUO_SETTINGS': {
        'IKEY': '',
        'SKEY': '',
        'AKEY': '',
        'HOST': '',
    },
    'WEATHERMAP_DATA': {
        'data': {},
        'config': {}
    }
}

USER_CONFIG = getattr(settings, 'OPENIPAM', {})
CONFIG = CONFIG_DEFAULTS.copy()
CONFIG.update(USER_CONFIG)
