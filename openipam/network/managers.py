from django.db.models import Model, Manager
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import utc, now
from django.db.models import Q

from netfields import NetManager

from guardian.shortcuts import get_objects_for_user

import random
import re
import operator


class NetworkManager(NetManager):

    def get_networks_owned_by_user(self, user, ids_only=False):
        networks = get_objects_for_user(user, 'network.is_owner_network')
        # networks = self.raw('''
        #     SELECT n.network FROM networks n
        #         INNER JOIN network_networkuserobjectpermission nup ON nup.content_object_id = n.network AND nup.user_id = %s
        #         INNER JOIN auth_permission nuap ON nup.permission_id = nuap.id AND nuap.codename = 'is_owner_network'

        #     UNION

        #     SELECT n.network FROM networks n
        #         INNER JOIN network_networkgroupobjectpermission ngp ON ngp.content_object_id = n.network
        #         INNER JOIN auth_permission ngap ON ngp.permission_id = ngap.id AND ngap.codename = 'is_owner_network'
        #         INNER JOIN users_groups ug ON ngp.group_id = ug.group_id and ug.user_id = %s
        # ''', [user.pk, user.pk])

        if ids_only:
            return tuple([str(network.network) for network in networks])
        else:
            return networks

    def get_networks_from_address_type(self, address_type):
        from openipam.network.models import NetworkRange

        # Get assigned ranges
        assigned_ranges = NetworkRange.objects.filter(address_ranges__isnull=False)

        # Get specific ranges on a address
        net_range = address_type.ranges.all()

        # If address has a range(s)
        if net_range:
            q_list = [Q(network__net_contained_or_equal=net.range) for net in net_range]
            return self.filter(reduce(operator.or_, q_list))
        # Otherwise try and get from default ranges
        elif address_type.is_default:
            q_list = [Q(network__net_contained_or_equal=net.range) for net in assigned_ranges]
            return self.exclude(reduce(operator.or_, q_list))
        else:
            return self.none()


class PoolManager(Manager):

    def get_default_pool(self):
        return self.get(is_default=True)


class LeaseManager(NetManager):

    def find_mac_from_lease(self, ip):
        return self.get(address__ip=ip).mac


class AddressManager(NetManager):

    def release_static_address(self, address):

        if not isinstance(address, Model):
            address = self.get(pk=address)

        if not address.mac:
            raise ValidationError('This address "%s" has already been released.' % address)

    def assign_ip6_address(self, mac, network):
    #def assign_ip6_address(self, mac, network, dhcp_server_id=0, use_lowest=False, is_server=False):

        from openipam.network.models import Network, Address, Pool

        # Sanity Checks for arguents
        if network and not isinstance(network, Model):
            network = Network.objects.get(pk=network)

        # if network.network.prefixlen == 64:
        #     # FIXME: the logic for choosing an address to try should go in a config file somewhere
        #     address_prefix = network.network.ip | (dhcp_server_id << 48)
        #     if not is_server:
        #         address_prefix |= 1 << 63
        #     address_prefix = address_prefix.make_net(48)

        # if network.network.prefixlen == 128:
        #     address = str(network.network)
        # Use lowest avaiable
        # elif use_lowest:

        net_str = str(network.network)
        address = Address.objects.raw('''
            SELECT (address+1) as next FROM addresses a1
            WHERE a1.address << %s
                AND NOT EXISTS (SELECT address from addresses a2
                            WHERE a2.address = (a1.address+1) and (a2.address+1) << %s)
            ORDER BY next
            LIMIT 1
        ''', [net_str, net_str])[0]

        if not address:
            raise ValidationError('Did not find an ip6 address?! network: %s prefixlen: %s mac: %s'
                                  % (net_str, network.network.prefixlen, mac))
        # else:
        #     macaddr = int('0x' + re.sub(mac,'[^0-9A-Fa-f]+',''))
        #     lastbits = (macaddr & 0xffffff) ^ (macaddr >> 24) | (random.getrandbits(24) << 24)
        #     address = address_prefix | lastbits

        # Check to see if it is used
        addr = Address.objects.filter(address=address)
        if addr:
            raise ValidationError('Address %r already in use' % addr)

        # Add our new address to the table
        Address.objects.create(mac=mac, network=network, address=address)

        return address

    def assign_static_address(self, mac, hostname=None, network=None, address=None):

        from openipam.network.models import Network, Pool
        from openipam.dns.models import DnsRecord

        # Sanity Checks for arguents
        if network and not isinstance(network, Model):
            network = Network.objects.get(pk=network)
        if address and not isinstance(address, Model):
            address = addresses = self.get(pk=address)

        # Validation checks on Network and Address
        if address and network:
            if address.address.version != network.network.version:
                raise ValidationError('Address and Network family mismatch: %s, %s' % (address, network))
            elif address.address not in network.network:
                raise ValidationError('Address %s does not belong to Network %s' % (address, network))

            # Since we have an address, we don't need a network
            network = None

        is_ipv4 = (address and address.address.version == 4) or (network and network.network.version == 4)

        # Get available address(es)
        if is_ipv4 is False:
            # We dont reuse IPV6
            addresses = None
        elif address:
            addresses = self.filter(pk=address, mac=None, reserved=False)
        elif network:
            addresses = self.filter(pk__net_contained=network, mac=None, reserved=False)

        # If no addresses available or IPV6
        if not addresses:

            # If ipv4
            if is_ipv4:
                # Find the assignable pools
                assignable_pools = Pool.objects.filter(assignable=True)
                # Filter addresses that and not asigned or reserved
                # And that are in assignable bools
                # And that leases are expired on never used or owned by the mac (user)
                pool_addresses = self.filter(
                    Q(lease__ends__lt=now()) | Q(lease__ends=None) | Q(lease__mac=mac),
                    mac=None,
                    reserved=False,
                    pool__in=assignable_pools,
                )

                # If network selected make sure addresses are in the network
                if network:
                    pool_addresses = pool_addresses.filter(address__net_contained=network)
                # If specific address specified, filter just to it
                if address:
                    pool_addresses = pool_addresses.filter(address=address)

                if not pool_addresses:
                    if address:
                        raise ValidationError('Could not assign IP address %s to MAC address %s. '
                                              ' It may be in use or not contained by a network.' % (address, mac))
                    else:
                        raise ValidationError('Could not assign IP address %s to MAC address %s. '
                                              ' There are no free addresses available with the'
                                              ' criteria specified.' % mac)

                # Select the first pool address to use
                new_address = pool_addresses[0]

                # Assign the mac to our selected address
                new_address.mac = mac
                new_address.save()

            # Else ipv6 address
            else:
                ip6net = address if address else network
                # Assign an ipv6 address to our mac
                new_address = self.assign_ip6_address(mac, ip6net)

        # Add the A record for this static (also adds PTR)
        if hostname:
            # delete any ptr's
            # FIXME: this is a sign that something wasn't deleted cleanly... maybe we shouldn't?
            #self.del_dns_record(name=openipam.iptypes.IP(address).reverseName()[:-1])
            # FIXME: is it safe to delete other DNS records here?
            tid = 1 if is_ipv4 else 28

            DnsRecord.objects.create(
                name=hostname,
                address=new_address,
                tid=tid
            )

        return new_address

