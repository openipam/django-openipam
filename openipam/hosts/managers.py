from django.db.models import Model, Manager, Q

from guardian.managers import UserObjectPermissionManager
from guardian.models import UserObjectPermission
from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms, get_perms_for_model

from netfields import NetManager


class HostManager(NetManager):

    def find_owners_of_host(self, mac):
        host = self.get(mac=mac)
        owners = get_users_with_perms(host, attach_perms=True, with_group_users=False)
        owners = [k for k, v in owners.items() if 'is_owner_host' in v]
        return owners

    def find_expiring_hosts(self):
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

    def get_hosts_with_owner_perms(self, user, **kwargs):

        if user.is_ipamadmin:
            return self.filter(**kwargs)
        else:

            domains_perms = self.raw('''
                SELECT DISTINCT h.* from hosts h

                WHERE h.mac IN (
                    SELECT mac from hosts h
                        INNER JOIN domains d ON h.hostname LIKE '%%.' || d.name
                        INNER JOIN dns_domaingroupobjectpermission dg ON dg.content_object_id = d.id
                        INNER JOIN users_groups ug ON ug.group_id = dg.group_id
                        INNER JOIN dns_domainuserobjectpermission du ON du.content_object_id = d.id
                        INNER JOIN auth_permission gp ON gp.id = dg.permission_id
                        INNER JOIN auth_permission up ON up.id = du.permission_id
                    WHERE
                        (du.user_id = %s OR ug.user_id = %s) AND
                        (gp.codename LIKE 'is_owner%%' OR up.codename LIKE 'is_owner%%')
                )''', [user.pk, user.pk])

            qs = self.filter(
                # Network Perms Join
                Q(
                    addresses__network__user_permissions__user=user,
                    addresses__network__user_permissions__permission__codename__in='is_owner_network'
                ) |
                # Domain Perms Join
                Q(
                    mac__in=[host.mac for host in domains_perms]
                ) |
                # Hosts Perm Join
                Q(
                    user_permissions__user=user,
                    user_permissions__permission__codename='is_owner_host'
                )
            )

            return qs.filter(**kwargs)

    def get_hosts_owned_by_user(self, user):
        return self.filter(
            Q(
                user_permissions__user=user,
                user_permissions__permission__codename='is_owner_host'
            ) |
            Q(
                group_permissions__in=user.groups.all(),
                group_permissions__permission__codename='is_owner_host'
            )
        )


        #return self.filter(user_permissions__user=user, user_permissions__permission__codename='is_owner_host')

    def get_hosts_by_user(self, user):
        return self.filter(
            user_permissions__user=user,
            user_permissions__permission__codename__in=['is_owner_host', 'change_host']
        )


