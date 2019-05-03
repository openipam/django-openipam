from django.db.models import Model, Manager
from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from guardian.shortcuts import get_objects_for_user

# from netfields import NetManager

import operator


class NetworkQuerySet(QuerySet):
    def can_view(self, user, use_groups=False, ids_only=False):
        User = get_user_model()

        # Temporarily set superuser to false so we can get only permission relations
        perm_user = User.objects.get(pk=user.pk)

        networks = get_objects_for_user(
            perm_user,
            "network.view_network",
            use_groups=use_groups,
            with_superuser=False,
        )

        if ids_only:
            return tuple([str(network.network) for network in networks])
        else:
            return networks

    def by_owner(self, user, use_groups=False, ids_only=False):
        User = get_user_model()

        # Temporarily set superuser to false so we can get only permission relations
        perm_user = User.objects.get(pk=user.pk)

        networks = get_objects_for_user(
            perm_user,
            "network.is_owner_network",
            use_groups=use_groups,
            with_superuser=False,
        )

        if ids_only:
            return tuple([str(network.network) for network in networks])
        else:
            return networks

    def by_change_perms(self, user, pk=None, ids_only=False):
        if user.has_perm("network.change_network") or user.has_perm(
            "network.is_owner_network"
        ):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            network_perms = get_objects_for_user(
                user,
                ["network.is_owner_network", "network.change_network"],
                any_perm=True,
            ).values_list("pk", flat=True)

            qs = self.filter(network__in=list(network_perms))

            if pk:
                qs = qs.filter(pk=pk).first()

            if ids_only:
                return tuple([network.network for network in qs])
            else:
                return qs

    def by_address_type(self, address_type):
        from openipam.network.models import NetworkRange

        # Get assigned ranges
        assigned_ranges = NetworkRange.objects.filter(address_ranges__isnull=False)

        # Get specific ranges on a address
        net_range = address_type.ranges.all() if address_type else None

        # Try and get from default ranges
        if address_type.is_default:
            q_list = [
                Q(network__net_contained_or_equal=net.range) for net in assigned_ranges
            ]
            return self.exclude(reduce(operator.or_, q_list))
        # Else If address has a range(s)
        elif net_range:
            q_list = [Q(network__net_contained_or_equal=net.range) for net in net_range]
            return self.filter(reduce(operator.or_, q_list))
        else:
            return self.none()


class NetworkManager(Manager):
    pass


class DhcpGroupManager(Manager):
    def get_queryset(self):
        qs = super(DhcpGroupManager, self).get_queryset()
        qs = qs.extra(select={"lname": "lower(name)"}).order_by("lname")
        return qs


class PoolManager(Manager):
    def get_default_pool(self):
        return self.get(is_default=True)


class LeaseManager(Manager):
    def find_mac_from_lease(self, ip):
        return self.get(address__ip=ip).mac


class AddressTypeManager(Manager):
    def get_by_name(self, name):
        return self.get(name__iexact=name)


class AddressQuerySet(QuerySet):
    def release(self, user=None, pool=False):
        from openipam.network.models import DefaultPool, Pool

        if not user:
            raise ValidationError("A user is required to delete hosts.")

        # Loop through addresses and release them
        for address in self:
            # Get default pool if false
            if pool is False:
                obj_pool = DefaultPool.objects.get_pool_default(address=address.address)
            # Assume an int if not Model
            elif not isinstance(pool, Model):
                obj_pool = Pool.objects.get(pk=pool)

            address.host = None
            address.pool = obj_pool
            address.changed_by = user
            address.changed = timezone.now()
            address.save()

        return self

    def by_dns_change_perms(self, user, pk=None):
        if user.has_perm("network.change_network") or user.has_perm(
            "network.is_owner_network"
        ):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            host_perms = get_objects_for_user(
                user, ["hosts.is_owner_host", "hosts.change_host"], any_perm=True
            ).values_list("pk", flat=True)
            network_perms = get_objects_for_user(
                user,
                [
                    "network.is_owner_network",
                    "network.add_records_to_network",
                    "network.change_network",
                ],
                any_perm=True,
            ).values_list("pk", flat=True)

            qs = self.filter(
                Q(host__mac__in=list(host_perms))
                | Q(network__network__in=list(network_perms))
            )

            if pk:
                qs = qs.filter(pk=pk).first()

            return qs


class AddressManager(Manager):
    pass


# class AddressManager(NetManager):

# TODO: Will we use the function below???

# def assign_ip6_address(self, mac, network):
#     from openipam.network.models import Network, Address, Pool

#     # Sanity Checks for arguents
#     if network and not isinstance(network, Model):
#         network = Network.objects.get(pk=network)

#     # if network.network.prefixlen == 64:
#     #     # FIXME: the logic for choosing an address to try should go in a config file somewhere
#     #     address_prefix = network.network.ip | (dhcp_server_id << 48)
#     #     if not is_server:
#     #         address_prefix |= 1 << 63
#     #     address_prefix = address_prefix.make_net(48)

#     # if network.network.prefixlen == 128:
#     #     address = str(network.network)
#     # Use lowest avaiable
#     # elif use_lowest:

#     net_str = str(network.network)
#     address = Address.objects.raw('''
#         SELECT (address+1) as next FROM addresses a1
#         WHERE a1.address << %s
#             AND NOT EXISTS (SELECT address from addresses a2
#                         WHERE a2.address = (a1.address+1) and (a2.address+1) << %s)
#         ORDER BY next
#         LIMIT 1
#     ''', [net_str, net_str])[0]

#     if not address:
#         raise ValidationError('Did not find an ip6 address?! network: %s prefixlen: %s mac: %s'
#                               % (net_str, network.network.prefixlen, mac))
#     # else:
#     #     macaddr = int('0x' + re.sub(mac,'[^0-9A-Fa-f]+',''))
#     #     lastbits = (macaddr & 0xffffff) ^ (macaddr >> 24) | (random.getrandbits(24) << 24)
#     #     address = address_prefix | lastbits

#     # Check to see if it is used
#     addr = Address.objects.filter(address=address)
#     if addr:
#         raise ValidationError('Address %r already in use' % addr)

#     # Add our new address to the table
#     Address.objects.create(mac=mac, network=network, address=address)

#     return address

# def assign_static_address(self, mac, hostname=None, network=None, address=None):
#     from openipam.network.models import Network, Pool
#     from openipam.dns.models import DnsRecord

#     # Sanity Checks for arguents
#     if network and not isinstance(network, Model):
#         network = Network.objects.get(pk=network)
#     if address and not isinstance(address, Model):
#         address = addresses = self.get(pk=address)

#     # Validation checks on Network and Address
#     if address and network:
#         if address.address.version != network.network.version:
#             raise ValidationError('Address and Network family mismatch: %s, %s' % (address, network))
#         elif address.address not in network.network:
#             raise ValidationError('Address %s does not belong to Network %s' % (address, network))

#         # Since we have an address, we don't need a network
#         network = None

#     is_ipv4 = (address and address.address.version == 4) or (network and network.network.version == 4)

#     # Get available address(es)
#     if is_ipv4 is False:
#         # We dont reuse IPV6
#         addresses = None
#     elif address:
#         addresses = self.filter(pk=address, mac=None, reserved=False)
#     elif network:
#         addresses = self.filter(pk__net_contained=network, mac=None, reserved=False)

#     # If no addresses available or IPV6
#     if not addresses:

#         # If ipv4
#         if is_ipv4:
#             # Find the assignable pools
#             assignable_pools = Pool.objects.filter(assignable=True)
#             # Filter addresses that and not asigned or reserved
#             # And that are in assignable bools
#             # And that leases are expired on never used or owned by the mac (user)
#             pool_addresses = self.filter(
#                 Q(lease__ends__lt=now()) | Q(lease__ends=None) | Q(lease__mac=mac),
#                 mac=None,
#                 reserved=False,
#                 pool__in=assignable_pools,
#             )

#             # If network selected make sure addresses are in the network
#             if network:
#                 pool_addresses = pool_addresses.filter(address__net_contained=network)
#             # If specific address specified, filter just to it
#             if address:
#                 pool_addresses = pool_addresses.filter(address=address)

#             if not pool_addresses:
#                 if address:
#                     raise ValidationError('Could not assign IP address %s to MAC address %s. '
#                                           ' It may be in use or not contained by a network.' % (address, mac))
#                 else:
#                     raise ValidationError('Could not assign IP address %s to MAC address %s. '
#                                           ' There are no free addresses available with the'
#                                           ' criteria specified.' % mac)

#             # Select the first pool address to use
#             new_address = pool_addresses[0]

#             # Assign the mac to our selected address
#             new_address.mac = mac
#             new_address.save()

#         # Else ipv6 address
#         else:
#             ip6net = address if address else network
#             # Assign an ipv6 address to our mac
#             new_address = self.assign_ip6_address(mac, ip6net)

#     # Add the A record for this static (also adds PTR)
#     if hostname:
#         # delete any ptr's
#         # FIXME: this is a sign that something wasn't deleted cleanly... maybe we shouldn't?
#         #self.del_dns_record(name=openipam.iptypes.IP(address).reverseName()[:-1])
#         # FIXME: is it safe to delete other DNS records here?
#         tid = 1 if is_ipv4 else 28

#         DnsRecord.objects.create(
#             name=hostname,
#             address=new_address,
#             tid=tid
#         )

#     return new_address


class DefaultPoolManager(Manager):
    def get_pool_default(self, address):
        # Find most specific DefaultPool for this address and return associated Pool
        pool = (
            self.filter(cidr__net_contains_or_equals=address).extra(
                select={"masklen": "masklen(cidr)"}, order_by=["-masklen"]
            )
        ).first()
        # first one should have the longest mask, which is most specific
        pool = pool.pool if pool else None
        return pool
