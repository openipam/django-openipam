from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Manager
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.timezone import utc, now
from django.conf import settings

from guardian.managers import UserObjectPermissionManager
from guardian.models import UserObjectPermission
from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms, get_perms_for_model

from netfields import NetManager

from openipam.network.models import Lease, Pool, Network, Address, DhcpGroup

from datetime import timedelta, datetime


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

    def get_hosts_owned_by_user(self, user):
        return self.filter(user_permissions__user=user, user_permissions__permission__codename='is_owner_host')

    def get_hosts_by_user(self, user):
        return self.filter(
            user_permissions__user=user,
            user_permissions__permission__codename__in=['is_owner_host', 'change_host']
        )


