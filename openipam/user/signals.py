from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.conf import settings
from guardian.models import UserObjectPermission, GroupObjectPermission


# Force Usernames to be lower case when being created
def force_usernames_uppercase(sender, instance, **kwargs):
    username = instance.username.lower()
    if username.startswith('a') and username[1:].isdigit() and len(username) == 9:
        instance.username = instance.username.upper()


# Automatically assign new users to IPAM_USER_GROUP
def assign_ipam_groups(sender, instance, created, **kwargs):
    # Get user group
    ipam_user_group = Group.objects.get_or_create(name=settings.IPAM_USER_GROUP)[0]
    # Check to make sure Admin Group exists
    ipam_admin_group = Group.objects.get_or_create(name=settings.IPAM_ADMIN_GROUP)[0]

    if created:
        instance.groups.add(ipam_user_group)


# Automatically remove permissions when user is deleted.
# This is only used when there are row level permissions defined using
# guadian tables.  Right now Host, Domain, DnsType, etc have explicit perm tables.
def remove_obj_perms_connected_with_user(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()
