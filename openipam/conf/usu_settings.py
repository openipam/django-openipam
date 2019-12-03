import ldap
from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType


LOCAL_AUTHENTICATION_BACKENDS = (
    # 'django_auth_ldap.backend.LDAPBackend',
    'openipam.core.backends.IPAMLDAPBackend',
)

AUTH_LDAP_SERVER_URI = 'ldaps://ldap.aggies.usu.edu:636'
AUTH_LDAP_BIND_DN = 'generic@aggies.usu.edu'
AUTH_LDAP_BIND_PASSWORD = '||||||||||||||||'
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    'ou=banner,dc=aggies,dc=usu,dc=edu',
    ldap.SCOPE_SUBTREE,
    '(&(memberOf:1.2.840.113556.1.4.1941:=CN=eduroam,OU=CustomGroups,DC=aggies,DC=usu,DC=edu)(sAMAccountName=%(user)s))'
)

# AUTH_LDAP_USER_DN_TEMPLATE = 'uid=%(user)s,ou=banner,dc=aggies,dc=usu,dc=edu'

AUTH_LDAP_GROUP_SEARCH = LDAPSearch('dc=aggies,dc=usu,dc=edu',
                                    ldap.SCOPE_SUBTREE, '(objectClass=group)')
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'eduPersonNickname',
    'last_name': 'sn',
    'email': 'usuPreferredEmailAddress',
}

AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_REQUIRE_CERT: False,
    ldap.OPT_REFERRALS: False,
}

# AUTH_LDAP_FIND_GROUP_PERMS = True
# AUTH_LDAP_CACHE_GROUPS = True
# AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_MIRROR_GROUPS = True
