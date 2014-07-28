from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection

from openipam.network.models import DhcpGroup, Pool
from openipam.conf.ipam_settings import CONFIG

from guardian.shortcuts import get_objects_for_user, get_objects_for_group, get_users_with_perms

from netfields import NetManager
from netfields.managers import NetWhere, NetQuery

import operator

User = get_user_model()


class HostMixin(object):
    def by_owner(self, user, use_groups=False, ids_only=False):

        # Temporarily set superuser to false so we can get only permission relations
        perm_user = User.objects.get(pk=user.pk)
        perm_user.is_superuser = False

        hosts = get_objects_for_user(perm_user, 'hosts.is_owner_host', use_groups=use_groups)

        if ids_only:
            return tuple([host.pk for host in hosts])
        else:
            return self.filter(pk__in=[host.pk for host in hosts])

    def by_group(self, group):
        hosts = get_objects_for_group(group, 'hosts.is_owner_host')
        return self.filter(pk__in=[host.pk for host in hosts])

    def by_change_perms(self, user, pk=None, ids_only=False):
        # If global permission set, then return all.
        if user.has_perm('hosts.change_host') or user.has_perm('hosts.is_owner_host'):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            host_perms = get_objects_for_user(user, ['hosts.is_owner_host', 'hosts.change_host'], any_perm=True).values_list('mac', flat=True)
            domain_perms = get_objects_for_user(user, ['dns.is_owner_domain', 'dns.change_domain'], any_perm=True).values_list('name', flat=True)
            network_perms = get_objects_for_user(user, ['network.is_owner_network', 'network.change_network'], any_perm=True).values_list('network', flat=True)

            qs = self.filter(
                Q(mac__in=host_perms) |
                Q(addresses__network__in=network_perms)
            )

            domain_q_list = [Q(hostname__endswith=name) for name in domain_perms]
            if domain_q_list:
                domain_qs = self.filter(reduce(operator.or_, domain_q_list))
                qs = qs | domain_qs

            if pk:
                qs = qs.filter(pk=pk).first()

            if ids_only:
                return tuple([host.pk for host in qs])
            else:
                return qs

    def by_expiring(self, ids_only=False, omit_guests=False):

        cursor = connection.cursor()
        try:
            cursor.execute('''
                SELECT DISTINCT h.mac from hosts h
                    CROSS JOIN notifications n
                    WHERE h.expires > now()
                        AND (h.last_notified IS NULL OR (now() - n.notification) > h.last_notified)
                        AND (h.expires - n.notification) < now()
                        AND UPPER("hosts"."hostname"::text) NOT LIKE UPPER(g-%)
                        AND UPPER("hosts"."hostname"::text) NOT LIKE UPPER(%.guests.usu.edu)



            ''')
            hosts = [host[0] for host in cursor.fetchall()]
        finally:
            cursor.close()

        if omit_guests is True:
            guest_hostname_prefix = CONFIG.get('GUEST_HOSTNAME_FORMAT')[0]
            guest_hostname_suffix = CONFIG.get('GUEST_HOSTNAME_FORMAT')[1]

            hosts = self.filter(mac__in=hosts).exclude(
                hostname__istartswith=guest_hostname_prefix,
                hostname__iendswith=guest_hostname_suffix
            )

        if ids_only is False:
            hosts = self.filter(mac__in=hosts)

        return hosts

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class HostQuerySet(QuerySet, HostMixin):
    pass


class HostManager(NetManager):

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

    def get_query_set(self):
        q = NetQuery(self.model, NetWhere)
        return HostQuerySet(self.model, q)

    def get_owners(self, mac):
        host = self.get(mac=mac)
        owners = get_users_with_perms(host, attach_perms=True, with_group_users=False)
        owners = [k for k, v in owners.items() if 'is_owner_host' in v]
        return owners

    #TODO!  Finish this and use it for everthing except the web form
    def add_or_update_host(self, user, hostname=None, mac=None, expire_days=None, expires=None, description=None, dhcp_group=False,
                           pool=False, ip_address=None, network=None, user_owners=None, group_owners=None, instance=None, full_clean=True):

        if isinstance(user, str):
            user = User.objects.get(username=user)

        if not instance and mac:
            instance = self.filter(mac=mac).first()
        if not instance:
            instance = self.model()

        instance.user = instance.changed_by = user

        # Set mac address
        if mac:
            instance.set_mac_address(mac)

        if hostname:
            instance.hostname = hostname

        if description is not None:
            instance.description = description

        if expires:
            instance.expires = expires
        elif expire_days:
            instance.set_expiration(expire_days)

        if dhcp_group:
            if isinstance(dhcp_group, int):
                dhcp_group = DhcpGroup.objects.get(pk=dhcp_group)
            elif isinstance(dhcp_group, str) or isinstance(dhcp_group, unicode):
                dhcp_group = DhcpGroup.objects.get(name=dhcp_group)
            instance.dhcp_group = dhcp_group
        elif dhcp_group is None:
            instance.dhcp_group = None

        address_type_pool = getattr(instance.address_type, 'pool', None)
        if pool:
            if isinstance(pool, int):
                pool = Pool.objects.get(pk=pool)
            elif isinstance(pool, str) or isinstance(pool, unicode):
                pool = Pool.objects.get(name=pool)
            instance.pool = pool
        elif pool is None:
            instance.pool = None
        elif address_type_pool:
            instance.pool = address_type_pool

        if ip_address:
            instance.ip_address = ip_address

        if network:
            instance.network = network

        if full_clean is True:
            instance.full_clean()
        instance.save()

        if instance.pool or instance.network or instance.ip_address:
            instance.set_network_ip_or_pool()
            instance.address_type_id = instance.address_type
            instance.save()

        if user_owners is not None or group_owners is not None:
            # Remove owners
            instance.remove_owners()
            user_groups = []

            if user_owners:
                if isinstance(user_owners, QuerySet):
                    users_to_add = user_owners
                elif isinstance(user_owners, list):
                    #u_list = [Q(username__iexact=user_owner) for user_owner in user_owners]
                    #users_to_add = User.objects.filter(reduce(operator.or_, u_list))
                    users_to_add = User.objects.filter(username__in=[user_owner for user_owner in user_owners])
                else:
                    #users_to_add = User.objects.filter(username__iexact=user_owners)
                    users_to_add = User.objects.filter(username=user_owners)
                users_to_add = list(users_to_add)
                user_groups += users_to_add

            if group_owners:
                if isinstance(group_owners, QuerySet):
                    groups_to_add = group_owners
                elif isinstance(group_owners, list):
                    #g_list = [Q(name__iexact=group_owner) for group_owner in group_owners]
                    #groups_to_add = Group.objects.filter(reduce(operator.or_, g_list))
                    groups_to_add = Group.objects.filter(name__in=[group_owner for group_owner in group_owners])
                else:
                    #groups_to_add = Group.objects.filter(name__iexact=group_owners)
                    groups_to_add = Group.objects.filter(name=group_owners)
                groups_to_add = list(groups_to_add)
                user_groups += groups_to_add

            if user_groups:
                for user_group in user_groups:
                    instance.assign_owner(user_group)

        # Make sure a user is assigned.
        has_users, has_groups = instance.get_owners()
        if not has_users and not has_groups:
            instance.assign_owner(user)

        return instance
