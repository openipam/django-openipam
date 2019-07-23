from django.contrib.auth.models import Group as AuthGroup, Permission
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from guardian.models import UserObjectPermission

from openipam.core.backends import IPAMLDAPBackend
from openipam.user.models import AuthSource

import gc
import ldap

User = get_user_model()


def get_objects_for_owner(user, app_label):
    owner_perm = Permission.objects.get(
        content_type__app_label=app_label, name="Is owner"
    )
    content_type = owner_perm.content_type
    model_class = content_type.model_class()
    user_objects = UserObjectPermission.objects.filter(
        user=user, content_type=content_type, permission=owner_perm
    ).values_list("object_pk")
    user_objects = [obj[0] for obj in user_objects]
    return model_class.objects.filter(pk__in=user_objects)


def fix_ldap_groups(test=False):
    url = settings.AUTH_LDAP_SERVER_URI
    dn = settings.AUTH_LDAP_BIND_DN
    pw = settings.AUTH_LDAP_BIND_PASSWORD
    conn = ldap.initialize(url)
    conn.set_option(ldap.OPT_REFERRALS, 0)
    conn.simple_bind_s(dn, pw)
    attrs = ["member"]

    ldap_source = AuthSource.objects.get(name="LDAP")

    counter = 0
    internal_groups = AuthGroup.objects.filter(source__source__name="INTERNAL")
    if test is True:
        print("Testing...")
    for group in internal_groups:
        result = conn.search_s(
            settings.AUTH_LDAP_GROUP_SEARCH.base_dn,
            ldap.SCOPE_SUBTREE,
            "cn=%s" % group.name,
            attrs,
        )
        group_result = result[0][0]
        if group_result:
            print(group_result)
            if test is False:
                group.source.source = ldap_source
                group.source.save()
                counter += 1

    print("%s Groups changed." % counter)


def sync_active_users():
    source = AuthSource.objects.get(name="LDAP")

    groups = AuthGroup.objects.filter(
        Q(permissions__isnull=False) | Q(groupobjectpermission__isnull=False),
        source__source=source,
    ).distinct()

    populate_user_from_ldap(groups=groups, force=True)


def populate_user_from_ldap(username=None, user=None, groups=[], force=False):
    ldap_backend = IPAMLDAPBackend()

    if username:
        return ldap_backend.populate_user(username=username)
    elif user:
        return ldap_backend.populate_user(username=user.username)
    elif groups:
        users = User.objects.filter(groups__in=groups)
    else:
        users = User.objects.all()

    for user in queryset_iterator(users):
        if not user.first_name or not user.last_name or not user.email or force is True:
            print(timezone.now(), "Updating user: %s" % user.username)
            ldap_backend.populate_user(username=user.username)
        else:
            print(timezone.now(), "NOT Updating user: %s" % user.username)


def queryset_iterator(queryset, chunksize=1000):
    """''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    """
    pk = 0
    last_pk = queryset.order_by("-pk")[0].pk
    queryset = queryset.order_by("pk")
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()
