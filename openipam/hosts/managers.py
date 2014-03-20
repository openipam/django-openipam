from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth import get_user_model

from guardian.shortcuts import get_objects_for_user, get_objects_for_group, get_users_with_perms

from netfields import NetManager

import operator

User = get_user_model()


class HostMixin(object):
    def by_owner(self, user):

        # Temporarily set superuser to false so we can get only permission relations
        perm_user = User.objects.get(pk=user.pk)
        perm_user.is_superuser = False

        return get_objects_for_user(perm_user, 'hosts.is_owner_host', klass=self, use_groups=True)

    def by_group(self, group):
        return get_objects_for_group(group, 'hosts.is_owner_host', klass=self)

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
        return HostQuerySet(self.model, using=self._db)

    def get_owners_of_host(self, mac):
        host = self.get(mac=mac)
        owners = get_users_with_perms(host, attach_perms=True, with_group_users=False)
        owners = [k for k, v in owners.items() if 'is_owner_host' in v]
        return owners

    def get_expiring_hosts(self):
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

    # def get_host_with_owner_perms(self, user, pk):

    #     if user.is_ipamadmin:
    #         qs = self.get(pk=pk)
    #         return qs if qs else None
    #     else:
    #         #user_groups = [group.pk for group in user.groups.all()]

    #         allowed_hosts = self.raw('''
    #             SELECT DISTINCT h.mac from hosts h
    #                 LEFT OUTER JOIN domains d ON h.hostname LIKE '%%.' || d.name
    #                 LEFT OUTER JOIN dns_domainuserobjectpermission dp ON d.id = dp.content_object_id
    #                 LEFT OUTER JOIN auth_permission dap ON dp.permission_id = dap.id
    #                 LEFT OUTER JOIN dns_domaingroupobjectpermission dgp ON d.id = dgp.content_object_id
    #                 LEFT OUTER JOIN auth_permission dgap ON dgp.permission_id = dgap.id
    #                 LEFT OUTER JOIN users_groups dug ON dgp.group_id = dug.group_id

    #                 LEFT OUTER JOIN addresses a ON h.mac = a.mac
    #                 LEFT OUTER JOIN networks n ON a.network = n.network
    #                 LEFT OUTER JOIN network_networkuserobjectpermission np ON n.network = np.content_object_id
    #                 LEFT OUTER JOIN auth_permission nap ON np.permission_id = nap.id
    #                 LEFT OUTER JOIN network_networkgroupobjectpermission ngp ON n.network = ngp.content_object_id
    #                 LEFT OUTER JOIN auth_permission ngap ON ngp.permission_id = ngap.id
    #                 LEFT OUTER JOIN users_groups nug ON ngp.group_id = nug.group_id

    #                 LEFT OUTER JOIN hosts_hostuserobjectpermission hp ON h.mac = hp.content_object_id
    #                 LEFT OUTER JOIN auth_permission hap ON hp.permission_id = hap.id
    #                 LEFT OUTER JOIN hosts_hostgroupobjectpermission hgp ON h.mac = hgp.content_object_id
    #                 LEFT OUTER JOIN auth_permission hgap ON hgp.permission_id = hgap.id
    #                 LEFT OUTER JOIN users_groups hug ON hgp.group_id = hug.group_id
    #             WHERE
    #                 h.mac = %(mac)s

    #                 AND
    #                 (
    #                     (dp.user_id = %(user_id)s AND dap.codename = 'is_owner_domain')
    #                     OR (dgap.codename = 'is_owner_domain' AND dug.user_id = %(user_id)s)

    #                     OR (np.user_id = %(user_id)s AND nap.codename = 'is_owner_network')
    #                     OR (ngap.codename = 'is_owner_network' AND nug.user_id = %(user_id)s)

    #                     OR (hp.user_id = %(user_id)s AND hap.codename = 'is_owner_host')
    #                     OR (hgap.codename = 'is_owner_host' AND hug.user_id = %(user_id)s)
    #                 )
    #         ''', {
    #             'user_id': user.pk,
    #             'mac': pk,
    #         })

    #         allowed_hosts = [host.mac for host in allowed_hosts]

    #         return self.get(mac=allowed_hosts[0]) if allowed_hosts else None


    def get_host_with_owner_perms(self, user, pk=None):
        if user.is_ipamadmin:
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            host_perms = user.host_owner_permissions
            domain_perms = user.domain_owner_permissions
            network_perms = user.network_owner_permissions

            qs = self.filter(
                Q(mac__in=host_perms) |
                Q(addresses__network__in=network_perms)
            )

            if user.domain_owner_permissions:
                domain_q_list = [Q(hostname__iendswith=domain) for domain in domain_perms]
                domain_qs = self.filter(reduce(operator.or_, domain_q_list))
                qs = qs | domain_qs

            if pk:
                qs = qs.filter(mac=pk)
                return qs[0] if qs else None
            else:
                return qs

    def get_hosts_owned_by_user(self, user, ids_only=False):

        # Temporarily set superuser to false so we can get only permission relations
        perm_user = User.objects.get(pk=user.pk)
        perm_user.is_superuser = False

        hosts = get_objects_for_user(perm_user, 'hosts.is_owner_host', use_groups=True)

        if ids_only:
            return tuple([host.pk for host in hosts])
        else:
            return hosts

