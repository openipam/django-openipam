from openipam.user.models import User, Permission, Group, UserToGroup, HostToGroup
from guardian.shortcuts import assign_perm
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup, Permission
from django.utils.timezone import utc
from guardian.models import UserObjectPermission
from datetime import datetime
import gc


def get_objects_for_owner(user, app_label, model_class):
    owner_perm = Permission.objects.get(content_type__app_label=app_label, codename='is_owner')
    content_type = ContentType.objects.get_for_model(model_class)
    user_objects = UserObjectPermission.objects.filter(user=user, content_type=content_type, permission=owner_perm).values_list('object_pk')
    user_objects = [obj[0] for obj in user_objects]
    return model_class.objects.filter(pk__in=user_objects)


def convert_host_permissions():
    hosts = (HostToGroup.objects.prefetch_related('gid__group_users')
             .filter(mac__expires__gte=datetime.utcnow().replace(tzinfo=utc)))

    for host in queryset_iterator(hosts):
        # Convert User Permissions (Group = user_A0000000)
        if host.gid.name.lower().startswith('user_'):
            users = host.gid.group_users.all()
            for user in users:
                username = user.uid.username.lower()
                #is_anumber = True if username.split('a')[-1].isdigit() else False

                # Convert owner permissions becuase thats all there is
                if user.host_permissions.name == 'OWNER':
                    try:
                        auth_user = AuthUser.objects.get(username=username)
                    except AuthUser.DoesNotExist:
                        auth_user = AuthUser(username=username)
                        auth_user.set_unusable_password()
                        auth_user.save()

                    # If these are local accounts, disable for now
                    # if not is_anumber:
                    #     auth_user.active = False
                    #     auth_user.save()

                    assign_perm('is_owner', auth_user, host.mac)
                else:
                    continue


def convert_users():
    users = User.objects.all()
    for user in queryset_iterator(users):
        auth_user, created = AuthUser.objects.get_or_create(
            username=user.username.lower()
        )
        if created:
            auth_user.active = False
            auth_user.set_unusable_password()
            auth_user.save()


# def convert_groups():
#     groups = Groups.objects.all()

#     for group in groups:


def queryset_iterator(queryset, chunksize=1000):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()
