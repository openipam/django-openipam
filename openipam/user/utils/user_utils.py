from django.contrib.auth.models import Group as AuthGroup, Permission
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import connection
from django.conf import settings

from guardian.shortcuts import assign_perm, remove_perm
from guardian.models import UserObjectPermission, GroupObjectPermission

from openipam.core.backends import IPAMLDAPBackend
from openipam.conf.ipam_settings import CONFIG
from openipam.user.models import GroupSource, AuthSource
from openipam.hosts.models import Host

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


def convert_groups():
    groups = Group.objects.exclude(name__istartswith="user_")
    source = AuthSource.objects.get(name="INTERNAL")

    converted_groups = []
    for group in groups:
        auth_group, created = AuthGroup.objects.get_or_create(name=group.name)
        if created:
            auth_group.source.source = source
            auth_group.source.save()
        else:
            GroupSource.objects.create(group=auth_group)

        converted_groups.append(AuthGroup.objects.get_or_create(name=group.name))

    for group in converted_groups:
        convert_permissions(groupname=group[0].name)


def convert_permissions(delete=False, groupname=None, user=None, username=None):

    if delete:
        GroupObjectPermission.objects.all().delete()

    # Base groups queryset, dont take user groups and the default group
    groups = (
        Group.objects.prefetch_related(
            "domains",
            "hosts",
            "networks",
            "pools",
            "user_groups",
            "user_groups__permissions",
        )
        .exclude(name__istartswith="user_")
        .exclude(name__in=["default", "guests"])
    )

    if groupname:
        groups = groups.filter(name__iexact=groupname)
    elif user:
        groups = groups.filter(user_groups__user=user)
    elif username:
        groups = groups.filter(user_groups__user__username__iexact=username)

    for group in groups:
        permissions = set([ug.permissions.name for ug in group.user_groups.all()])
        auth_group, created = AuthGroup.objects.get_or_create(name=group.name)

        hosts = group.hosts.all()
        domains = group.domains.all()
        networks = group.networks.all()
        pools = group.pools.all()
        user_groups = group.user_groups.all()

        if user:
            user_groups = user_groups.filter(user=user)
        elif username:
            user_groups = user_groups.filter(user__username__iexact=username)

        if permissions:
            # Only owner permission is needed for hosts
            if "OWNER" in permissions:
                print(
                    "Assigning owner permission on group %s for hosts \n" % auth_group
                )
                _assign_perms(
                    "is_owner",
                    auth_group,
                    hosts=hosts,
                    domains=domains,
                    networks=networks,
                )

                # Assign users to this group
                for user in user_groups.filter(permissions__name="OWNER"):
                    user.user.groups.add(auth_group)

            if "ADD" in permissions:
                # IF there is just ADD only then stick the permission on the group
                if len(permissions) == 1:
                    print(
                        "Assigning add records permission on group %s for domains \n"
                        % auth_group
                    )
                    _assign_perms(
                        "add_records_to",
                        auth_group,
                        domains=domains,
                        networks=networks,
                        pools=pools,
                    )

                    # Assign users to this group
                    for user in user_groups.filter(permissions__name="ADD"):
                        user.user.groups.add(auth_group)

                # Otherwise if there are multiple groups, then we put ADD permission on user for now
                else:
                    users = user_groups.filter(permissions__name="ADD")
                    for user in users:
                        # Force superuser to false to force insert
                        user.is_superuser = False
                        print(
                            "Assigning add records permission on user %s for domains, networks, and pools \n"
                            % user.user
                        )
                        _assign_perms(
                            "add_records_to",
                            user.user,
                            domains=domains,
                            networks=networks,
                            pools=pools,
                        )


def convert_min_permissions(user=None, username=None):
    user_qs = User.objects.all()
    if user:
        user_qs = user_qs.filter(pk=user.pk)
    elif username:
        user_qs = user_qs.filter(username__iexact=username)

    # Add admins to IPAM admins
    ipam_admin_group = AuthGroup.objects.get(name=CONFIG.get("ADMIN_GROUP"))
    users_ipam_admins = user_qs.filter(min_permissions__name="ADMIN")
    for user in users_ipam_admins:
        user.groups.add(ipam_admin_group)

    # Add DEITY users as super admins
    users_deity = user_qs.filter(min_permissions__name="DEITY")
    for user in users_deity:
        user.is_superadmin = True
        user.save()


def _assign_perms(
    permission, user_or_group, hosts=[], domains=[], networks=[], pools=[]
):
    for host in hosts:
        assign_perm("hosts.%s_host" % permission, user_or_group, host)
    for domain in domains:
        assign_perm("dns.%s_domain" % permission, user_or_group, domain)
    for network in networks:
        assign_perm("network.%s_network" % permission, user_or_group, network)
    # print('pools - %s' % len(pools))
    # for pool in pools:
    #     print(pool)
    #     assign_perm('network.%s_pool' % permission, user_or_group, pool)

    return


def convert_host_permissions(
    delete=False, username=None, host_pk=None, on_empty_only=False
):
    owner_perm = Permission.objects.get(
        content_type__app_label="hosts", codename="is_owner_host"
    )
    host_type = ContentType.objects.get(app_label="hosts", model="host")

    # First delete to make a clean slate
    if delete:
        remove_perm("hosts.is_owner_host", Host)
        # HostUserObjectPermission.objects.filter(permission=owner_perm).delete()
        # HostGroupObjectPermission.objects.filter(permission=owner_perm).delete()
    if host_pk:
        if on_empty_only:
            host = Host.objects.filter(pk=host_pk).first()
            if not host:
                return
            user_owners, group_owners = host.owners
            if user_owners or group_owners:
                return
        host_groups = (
            HostToGroup.objects.select_related("host")
            .prefetch_related("group__user_groups")
            .filter(host__pk=host_pk)
        )
    elif username:
        host_groups = (
            HostToGroup.objects.select_related("host")
            .prefetch_related("group__user_groups")
            .filter(group__name__iexact="user_%s" % username)
        )
    else:
        host_groups = (
            HostToGroup.objects.select_related("host")
            .prefetch_related("group__user_groups")
            .filter(host__expires__gte=timezone.now)
        )

    if host_groups:
        for host_group in queryset_iterator(host_groups):
            # Convert User Permissions (Group = user_A0000000)
            if host_group.group.name.lower().startswith("user_"):
                users = host_group.group.user_groups.select_related().all()
                for user in users:
                    username = user.user.username
                    # is_anumber = True if username.split('a')[-1].isdigit() else False

                    # Convert owner permissions becuase thats all there is
                    if user.host_permissions.name == "OWNER":
                        # ry:
                        auth_user, created = User.objects.get_or_create(
                            username__iexact=username
                        )
                        # Force superuser to false to force an insert
                        auth_user.is_superuser = False
                        # except User.DoesNotExist:
                        #     auth_user = User(username=username)
                        #     auth_user.set_unusable_password()
                        #     auth_user.save()

                        # If these are local accounts, disable for now
                        # if not is_anumber:
                        #     auth_user.active = False
                        #     auth_user.save()
                        if not auth_user.has_perm("is_owner_host", host_group.host):
                            print(
                                "Assigning owner permission to user %s for host %s \n"
                                % (auth_user, host_group.host)
                            )
                            # UserObjectPermission.objects.get_or_create(
                            #     user=auth_user,
                            #     permission=owner_perm,
                            #     object_pk=host_group.mac.pk,
                            #     content_type=host_type,
                            # )
                            assign_perm(
                                "hosts.is_owner_host", auth_user, host_group.host
                            )
                    else:
                        continue
            else:
                auth_group, created = AuthGroup.objects.get_or_create(
                    name=host_group.group.name
                )
                # if not auth_group.has_perm('is_owner_host', host_group.host):
                print(
                    "Assigning owner permission to group %s for host %s \n"
                    % (auth_group, host_group.host)
                )
                # GroupObjectPermission.objects.get_or_create(
                #     group=auth_group,
                #     permission=owner_perm,
                #     object_pk=host_group.mac.pk,
                #     content_type=host_type,
                # )
                assign_perm("hosts.is_owner_host", auth_group, host_group.host)


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


# Not needed anymore because we switched django user model
# def convert_users():
#     users = User.objects.all()
#     for user in queryset_iterator(users):
#         auth_user, created = AuthUser.objects.get_or_create(
#             username=user.username.lower()
#         )
#         if created:
#             auth_user.active = False
#             auth_user.set_unusable_password()
#             auth_user.save()


# def convert_groups():
#     groups = Groups.objects.all()

#     for group in groups:


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
