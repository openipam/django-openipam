from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth import get_user_model

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
            return hosts

    def by_group(self, group):
        return get_objects_for_group(group, 'hosts.is_owner_host', klass=self)

    def by_change_perms(self, user, pk=None):
        if user.has_perm('hosts.change_host'):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            host_perms = user.host_owner_perms
            domain_perms = user.domain_owner_perms
            network_perms = user.network_owner_perms

            qs = self.filter(
                Q(mac__in=host_perms) |
                Q(addresses__network__in=network_perms)
            )

            if domain_perms:
                domain_q_list = [Q(hostname__iendswith=domain) for domain in domain_perms]
                domain_qs = self.filter(reduce(operator.or_, domain_q_list))
                qs = qs | domain_qs

            if pk:
                qs = qs.filter(mac=pk)
                return qs[0] if qs else None
            else:
                return qs

    def expiring(self):
        host_macs = self.raw('''
            SELECT DISTINCT h.mac, h.hostname, h.expires, h.description, n.notification
            FROM hosts h
                INNER JOIN notifications_to_hosts nh ON (h.mac = nh.mac)
                INNER JOIN notifications n ON (n.id = nh.nid)
                INNER JOIN addresses a ON (h.mac = a.mac)
                WHERE (h.expires - n.notification) <= now()
        ''')
        host_macs = [host.mac for host in host_macs]
        hosts = self.filter(mac__in=host_macs)
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


    # def get_hosts_owned_by_user(self, user, ids_only=False):

    #     # Temporarily set superuser to false so we can get only permission relations
    #     perm_user = User.objects.get(pk=user.pk)
    #     perm_user.is_superuser = False

    #     hosts = get_objects_for_user(perm_user, 'hosts.is_owner_host', use_groups=True)

    #     if ids_only:
    #         return tuple([host.pk for host in hosts])
    #     else:
    #         return hosts
