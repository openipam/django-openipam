from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.conf import settings

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
    from openipam.user.models import Group

    user_utils.convert_permissions(user=user)
    # We do this on the host view instead for performance
    #user_utils.convert_host_permissions(username=user.username)
    user_utils.convert_min_permissions(user=user)


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


# Automatically add permissions to master Guardian user table from direct relations
# Used in the admin UI
def add_user_object_permission(sender, instance, created, **kwargs):
    if sender.__name__.lower() in DIRECT_USER_PERM_RELATIONS and created:
        content_type = ContentType.objects.get_for_model(instance.content_object)

        UserObjectPermission.objects.get_or_create(
            object_pk=instance.content_object_id,
            content_type=content_type,
            user=instance.user,
            permission=instance.permission
        )


# Automatically add permissions to master Guardian group table from direct relations
# Used in the admin UI
def add_group_object_permission(sender, instance, created, **kwargs):
    if sender.__name__.lower() in DIRECT_GROUP_PERM_RELATIONS and created:
        content_type = ContentType.objects.get_for_model(instance.content_object)

        GroupObjectPermission.objects.get_or_create(
            object_pk=instance.content_object_id,
            content_type=content_type,
            group=instance.group,
            permission=instance.permission
        )


# Automatically remove permissions to master Guardian user table from direct relations
# Used in the admin UI
def remove_user_object_permission(sender, instance, **kwargs):
    if sender.__name__.lower() in DIRECT_USER_PERM_RELATIONS:
        content_type = ContentType.objects.get_for_model(instance.content_object)

        try:
            UserObjectPermission.objects.get(
                object_pk=instance.content_object_id,
                content_type=content_type,
                user=instance.user,
                permission=instance.permission
            ).delete()
        except UserObjectPermission.DoesNotExist:
            pass


# Automatically remove permissions to master Guardian group table from direct relations
# Used in the admin UI
def remove_group_object_permission(sender, instance, **kwargs):
    if sender.__name__.lower() in DIRECT_GROUP_PERM_RELATIONS:
        content_type = ContentType.objects.get_for_model(instance.content_object)

        try:
            GroupObjectPermission.objects.get(
                object_pk=instance.content_object_id,
                content_type=content_type,
                group=instance.group,
                permission=instance.permission
            ).delete()
        except GroupObjectPermission.DoesNotExist:
            pass


def add_direct_user_object_permission(sender, instance, created, **kwargs):
    content_types = ContentType.objects.filter(
        app_label__in=DIRECT_PERM_APPS,
        model__in=DIRECT_PERM_MODELS
    )

    if created and instance.content_type in content_types:
        ModelObject = instance.content_type.model_class()
        model_object = ModelObject.objects.get(pk=instance.object_pk)
        model_object.user_permissions.get_or_create(
            user=instance.user,
            permission=instance.permission
        )


def add_direct_group_object_permission(sender, instance, created, **kwargs):
    content_types = ContentType.objects.filter(
        app_label__in=DIRECT_PERM_APPS,
        model__in=DIRECT_PERM_MODELS
    )

    if created and instance.content_type in content_types:
        ModelObject = instance.content_type.model_class()
        model_object = ModelObject.objects.get(pk=instance.object_pk)
        model_object.group_permissions.get_or_create(
            group=instance.group,
            permission=instance.permission
        )


def remove_direct_user_object_permission(sender, instance, **kwargs):
    content_types = ContentType.objects.filter(
        app_label__in=DIRECT_PERM_APPS,
        model__in=DIRECT_PERM_MODELS
    )

    if instance.content_type in content_types:
        ModelObject = instance.content_type.model_class()
        try:
            model_object = ModelObject.objects.get(pk=instance.object_pk)
            model_object.user_permissions.filter(
                user=instance.user,
                permission=instance.permission
            ).delete()
        except ModelObject.DoesNotExist:
            pass


def remove_direct_group_object_permission(sender, instance, **kwargs):
    content_types = ContentType.objects.filter(
        app_label__in=DIRECT_PERM_APPS,
        model__in=DIRECT_PERM_MODELS
    )

    if instance.content_type in content_types:
        ModelObject = instance.content_type.model_class()
        try:
            model_object = ModelObject.objects.get(pk=instance.object_pk)
            model_object.group_permissions.filter(
                group=instance.group,
                permission=instance.permission
            ).delete()
        except ModelObject.DoesNotExist:
            pass
