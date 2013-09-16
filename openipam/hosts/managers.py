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
        owners = [k for k, v in owners.items() if 'is_owner' in v]
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

    @transaction.commit_on_success
    def update_registration(self, changed_by, mac, new_mac=None, hostname=None, description=None,
                    expires=None, expiration_format=None, network=None, address=None,
                    owners=None, groups=None, dhcp_group=None, pool=None):

        from openipam.hosts.models import Disabled

        # Get objects if IDs are passed
        if network and not isinstance(network, Model):
            network = Network.objects.get(pk=network)
        if address and not isinstance(address, Model):
            address = Address.objects.get(pk=address)
        if owners and not isinstance(owners[0], Model):
            owners = User.objects.filter(pk__in=owners)
        if groups and not isinstance(groups[0], Model):
            groups = Group.objects.filter(pk__in=groups)
        if dhcp_group and isinstance(dhcp_group, Model):
            dhcp_group = DhcpGroup.objects.get(pk=dhcp_group)
        if pool and not isinstance(pool, Model):
            pool = Pool.objects.get(pk=pool)

        # Network and address sanity checks
        if address and network:
            if address.address in network.network:
                network = None
            else:
                raise ValidationError('The address %s does not belong to the network %s' % (address, network))

        # Expires checks and convertion
        if expires:
            try:
                assert int(expires)
            except AssertionError:
                raise ValidationError('The expires arguments needs to be an integer expressed in days.')
            expires = datetime.combine(now(), time(6).replace(tzinfo=utc)) + timedelta(days=expires)

        # Check if host is disabled
        mac_is_disabled = Disabled.objects.filter(mac=new_mac) if new_mac else False
        if mac_is_disabled:
            raise ValidationError('This host is disabled (mac: %s)' % new_mac)

        # Get host to change
        host = self.get(pk=mac)

        current_pool = host.pools.all()
        if len(current_pool) > 1:
            raise ValidationError('Host has multiple pools assigned. This should not happen, please contact an IPAM admin')
        current_pool = current_pool[0] if current_pool else None

        # Release addresses associated with this host if we are moving to dynamic assignment
        if pool and not current_pool:
            Address.objects.filter(mac=mac).release()

        # If pool is changing, perform the m2m operations
        if pool and pool != current_pool:
            host.pools.clear()
            host.pools.add(pool)


        # Update fields
        host.change_by = changed_by
        host.mac = new_mac if new_mac else mac
        if hostname:
            host.hostname = hostname
        if description:
            host.description = description
        if expires:
            host.expires = expires
        if dhcp_group:
            host.dhcp_group = dhcp_group
