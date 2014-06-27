from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from openipam.conf.ipam_settings import CONFIG
from guardian.models import UserObjectPermission, GroupObjectPermission


DIRECT_PERM_MODELS_LIST = (
    ('hosts', 'host'),
    ('dns', 'domain'),
    ('dns', 'dnstype'),
    ('network', 'network'),
)
DIRECT_PERM_APPS = [app[0] for app in DIRECT_PERM_MODELS_LIST]
DIRECT_PERM_MODELS = [model[1] for model in DIRECT_PERM_MODELS_LIST]
DIRECT_USER_PERM_RELATIONS = ['%suserobjectpermission' % model[1] for model in DIRECT_PERM_MODELS_LIST]
DIRECT_GROUP_PERM_RELATIONS = ['%sgroupobjectpermission' % model[1] for model in DIRECT_PERM_MODELS_LIST]


# Force Usernames to be lower case when being created
def force_usernames_uppercase(sender, instance, **kwargs):
    username = instance.username.lower()
    if username.startswith('a') and username[1:].isdigit() and len(username) == 9:
        instance.username = instance.username.upper()


# Convert Host permissions on login.
def convert_user_permissions(sender, request, user, **kwargs):
    from openipam.user.utils import user_utils

    user_utils.convert_permissions(user=user)
    # We do this on the host view instead for performance
    #user_utils.convert_host_permissions(username=user.username)
    user_utils.convert_min_permissions(user=user)

    # Convert groups for IPAM admins.
    if user.is_ipamadmin:
        user_utils.convert_groups()


# Automatically assign new users to IPAM_USER_GROUP
def assign_ipam_groups(sender, instance, created, **kwargs):
    # Get user group
    ipam_user_group = Group.objects.get_or_create(name=CONFIG.get('USER_GROUP'))[0]
    # Check to make sure Admin Group exists
    # ipam_admin_group = Group.objects.get_or_create(name=settings.IPAM_ADMIN_GROUP)[0]

    # Get user groups
    user_groups = instance.groups.all()

    if ipam_user_group not in user_groups:
        instance.groups.add(ipam_user_group)


# Automatically remove permissions when user is deleted.
# This is only used when there are row level permissions defined using
# guadian tables.  Right now Host, Domain, DnsType, etc have explicit perm tables.
def remove_obj_perms_connected_with_user(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

