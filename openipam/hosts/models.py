from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete, post_save
from django.core.validators import validate_ipv46_address
from django.utils.functional import cached_property

from netfields import InetAddressField, MACAddressField, NetManager
from netaddr.core import AddrFormatError

from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms, \
    get_groups_with_perms, remove_perm, assign_perm

from openipam.core.mixins import DirtyFieldsMixin
from openipam.hosts.validators import validate_hostname
from openipam.hosts.managers import HostManager
from openipam.user.signals import remove_obj_perms_connected_with_user

from datetime import datetime, timedelta

import string
import random


class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    structured = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    validation = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'attributes'


class AttributeToHost(models.Model):
    attribute = models.IntegerField(null=True, blank=True, db_column='aid')
    name = models.CharField(max_length=255, blank=True, null=True)
    structured = models.BooleanField(default=None)
    required = models.BooleanField(default=False)
    mac = MACAddressField(blank=True, null=True)
    avid = models.IntegerField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    objects = NetManager()

    def __unicode__(self):
        return '%s %s' % (self.attribute.name, self.name)

    class Meta:
        managed = False
        db_table = 'attributes_to_hosts'


class Disabled(models.Model):
    host = models.ForeignKey('Host', primary_key=True, db_column='mac', db_constraint=False, related_name='disabled_host')
    reason = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True, db_column='disabled')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='disabled_by')

    def __unicode__(self):
        return self.pk

    class Meta:
        db_table = 'disabled'
        verbose_name = 'Disabled Host'
        ordering = ('-changed',)


class ExpirationType(models.Model):
    expiration = models.DateTimeField()
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')

    def __unicode__(self):
        return '%s days' % self.expiration.days

    class Meta:
        db_table = 'expiration_types'
        ordering = ('expiration',)


class FreeformAttributeToHost(models.Model):
    host = models.ForeignKey('Host', db_column='mac', related_name='freeform_attributes')
    attribute = models.ForeignKey('Attribute', db_column='aid')
    value = models.TextField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    def __unicode__(self):
        return '%s %s %s' % (self.host.hostname, self.attribute.name, self.value)

    class Meta:
        db_table = 'freeform_attributes_to_hosts'


class GuestTicket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='uid')
    ticket = models.CharField(max_length=255, unique=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.ticket

    def set_ticket(self):
        """Generates a human-readable string for a ticket."""

        def generate_random_ticket():
            vowels = ("a", "e", "i", "o", "u")
            consonants = [a for a in string.ascii_lowercase if a not in vowels]
            groups = ("th", "ch", "sh", "kl", "gr", "br")

            num_vowels = len(vowels) - 1
            num_consonants = len(consonants) - 1
            num_groups = len(groups) - 1

            vowel = []
            cons = []
            group = []

            for i in range(4):
                vowel.append(vowels[random.randint(0, num_vowels)])
                cons.append(consonants[random.randint(0, num_consonants)])
                group.append(groups[random.randint(0, num_groups)])

            structure = []
            structure.append('%s%s%s%s%s%s%s%s' % (cons[0], vowel[0], cons[1], cons[2], vowel[1], cons[3], vowel[2], group[0]))
            structure.append('%s%s%s%s%s%s' % (group[0], vowel[0], cons[0], cons[1], vowel[1], group[1]))
            structure.append('%s%s%s%s%s' % (group[0], vowel[0], cons[0], vowel[1], "s"))
            structure.append('%s%s%s%s%s' % (vowel[0], group[0], vowel[1], cons[0], vowel[2]))
            structure.append('%s%s%s%s%s' % (group[0], vowel[0], cons[0], vowel[1], group[1]))
            structure.append('%s%s%s%s' % (vowel[0], group[0], vowel[1], group[1]))
            structure.append('%s%s%s%s%s%s%s%s' % (cons[0], vowel[0], cons[1], vowel[1], cons[2], vowel[2], cons[3], vowel[2]))
            structure.append('%s%s%s%s%s' % (group[0], vowel[1], group[1], vowel[1], cons[0]))

            return structure[random.randint(0, len(structure)-1)]

        ticket = generate_random_ticket()
        while GuestTicket.objects.filter(ticket=ticket):
            ticket = generate_random_ticket()

        self.ticket = ticket

    class Meta:
        db_table = 'guest_tickets'


class GulRecentArpByaddress(models.Model):
    host = models.ForeignKey('Host', db_column='mac', db_constraint=False, related_name='ip_history', primary_key=True)
    address = InetAddressField()
    stopstamp = models.DateTimeField()

    objects = NetManager()

    def __unicode__(self):
        return '%s - %s' % (self.pk, self.address)

    class Meta:
        db_table = 'gul_recent_arp_byaddress'


class GulRecentArpBymac(models.Model):
    host = models.ForeignKey('Host', db_column='mac', db_constraint=False, related_name='mac_history', primary_key=True)
    address = InetAddressField()
    stopstamp = models.DateTimeField()

    objects = NetManager()

    def __unicode__(self):
        return '%s - %s' % (self.pk, self.address)

    class Meta:
        db_table = 'gul_recent_arp_bymac'


class Host(DirtyFieldsMixin, models.Model):
    mac = MACAddressField('Mac Address', primary_key=True)
    hostname = models.CharField(max_length=255, unique=True, validators=[validate_hostname], db_index=True)
    description = models.TextField(blank=True, null=True)
    address_type_id = models.ForeignKey('network.AddressType', blank=True, null=True, db_column='address_type_id',
                                        on_delete=models.SET_NULL)
    pools = models.ManyToManyField('network.Pool', through='network.HostToPool',
                                   related_name='pool_hosts', blank=True, null=True)
    #freeform_attributes = models.ManyToManyField('Attribute', through='FreeformAttributeToHost',
    #                                             related_name='freeform_hosts',  blank=True, null=True)
    #structured_attributes = models.ManyToManyField('Attribute', through='StructuredAttributeToHost',
    #                                               related_name='structured_hosts',  blank=True, null=True)
    dhcp_group = models.ForeignKey('network.DhcpGroup', db_column='dhcp_group',
                                   verbose_name='DHCP Group', blank=True, null=True, on_delete=models.SET_NULL)
    expires = models.DateTimeField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')
    last_notified = models.DateTimeField(blank=True, null=True)

    objects = HostManager()

    def __init__(self, *args, **kwargs):

        # Initialize setters
        self._expire_days = None
        self._user_owners = None
        self._group_owners = None
        self._user = None

        self.ip_address = None
        self.pool = None
        self.network = None

        super(Host, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.hostname

    # Overload getattr for get original values
    def __getattr__(self, name):
        if name.startswith('original_') and name.split('_')[1] in self._original_state.keys():
            def _original(fieldname):
                fieldvalue = self._original_state.get(fieldname, None)
                if fieldvalue is not None:
                    return fieldvalue
            return _original(name.split('_')[1])
        else:
            raise AttributeError("%r object has no attribute %r" % (self.__class__, name))

    @cached_property
    def _addresses_cache(self):
        return list(self.addresses.all())

    @cached_property
    def _pools_cache(self):
        return list(self.pools.all())

    @property
    def expire_days(self):
        if self._expire_days:
            return self._expire_days
        else:
            return self.get_expire_days()

    @expire_days.setter
    def expire_days(self, days):
        self._expire_days = days

    @cached_property
    def owners(self):
        return self.get_owners(ids_only=False)

    def get_owners(self, ids_only=True, owner_detail=False, users_only=False):
        users_dict = get_users_with_perms(self, attach_perms=True, with_group_users=False)
        groups_dict = get_groups_with_perms(self, attach_perms=True)

        users = []
        for user, permissions in users_dict.iteritems():
            if 'is_owner_host' in permissions:
                users.append(user)

        groups = []
        for group, permissions in groups_dict.iteritems():
            if 'is_owner_host' in permissions:
                groups.append(group)

        if users_only:
            User = get_user_model()
            users_from_groups = [user for user in User.objects.filter(groups__in=groups)]
            users = list(set(users + users_from_groups))
            return users

        if owner_detail:
            users = [(user.pk, user.username, user.get_full_name(), user.email) for user in users]
            groups = [(group.pk, group.name) for group in groups]

        elif ids_only:
            users = [user.pk for user in users]
            groups = [group.pk for group in groups]

        return users, groups

    @property
    def user_owners(self):
        if self._user_owners:
            return self._user_owners
        else:
            return [owner.username for owner in self.owners[0]]

    @user_owners.setter
    def user_owners(self, owners):
        self._user_owners = owners

    @property
    def user(self):
        if self._user:
            return self._user
        else:
            return self.changed_by

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def group_owners(self):
        if self._group_owners:
            return self._group_owners
        else:
            return [owner.name for owner in self.owners[1]]

    @group_owners.setter
    def group_owners(self, owners):
        self._group_owners = owners

    @property
    def is_dynamic(self):
        if self.is_dirty() is False:
            return True if self._pools_cache else False
        else:
            return True if self.pools.all() else False

    @property
    def is_static(self):
        return True if self.is_dynamic is False else False

    @property
    def is_disabled(self):
        return True if Disabled.objects.filter(host=self.pk) else False

    @property
    def is_expired(self):
        return True if self.expires < timezone.now() else False

    @property
    def address_type(self):
        # Get and Set address type if receord is not new.
        if self.pk and not self.address_type_id:
            from openipam.network.models import AddressType, NetworkRange

            addresses = self.addresses.all()
            pools = self.pools.all()

            try:
                # if (len(addresses) + len(pools)) > 1:
                #     self.address_type = None
                # elif addresses:
                if addresses:
                    try:
                        ranges = NetworkRange.objects.filter(range__net_contains_or_equals=addresses[0].address)
                        if ranges:
                            self.address_type_id = AddressType.objects.get(ranges__in=ranges)
                        else:
                            raise AddressType.DoesNotExist
                    except AddressType.DoesNotExist:
                        self.address_type_id = AddressType.objects.get(is_default=True)
                elif pools:
                    self.address_type_id = AddressType.objects.get(pool=pools[0])
            except AddressType.DoesNotExist:
                self.address_type_id = None

        return self.address_type_id

    @address_type.setter
    def address_type(self, value):
        self.address_type_id = value

    @property
    def mac_stripped(self):
        mac = str(self.mac)
        mac = [c for c in mac if c.isdigit() or c.isalpha()]
        return ''.join(mac)

    @property
    def mac_last_seen(self):
        # if self.gul_recent_arp_bymac is None:
        #     self.gul_recent_arp_bymac = GulRecentArpBymac.objects.all()

        #gul_mac = filter(lambda x: x.mac == self.mac, self.gul_recent_arp_bymac)
        gul_mac = GulRecentArpBymac.objects.filter(mac=self.mac).order_by('-stopstamp')

        if gul_mac:
            return gul_mac[0].stopstamp
        else:
            return None

    @cached_property
    def master_ip_address(self):
        if self.is_static:
            if not self.ip_addresses:
                return None
            elif len(self.ip_addresses) == 1:
                return self.ip_addresses[0]
            else:
                address = self.addresses.filter(arecords__name=self.hostname).first()
                return str(address) if address else self.ip_addresses[0]
        return None

    @cached_property
    def ip_addresses(self):
        return [str(address) for address in self.addresses.all()]

    def add_ip_address(self, user=None, ip_address=None, network=None, hostname=None):
        from openipam.network.models import Network, Address
        from openipam.dns.models import DnsRecord, DnsType

        address = None

        if not hostname:
            raise ValidationError('A hostname is required.')

         # Check to see if hostname already taken
        used_hostname = DnsRecord.objects.filter(
            dns_type__in=[DnsType.objects.A, DnsType.objects.AAAA],
            name=hostname
        ).first()
        if used_hostname:
            raise ValidationError('Hostname %s is already assigned to Address %s.' % (hostname, used_hostname.ip_content))

        if not user and self.user:
            user = self.user
        elif not user:
            raise Exception('A User must be specified to an address to this host.')

        user_pools = get_objects_for_user(
            user,
            ['network.add_records_to_pool', 'network.change_pool'],
            any_perm=True
        )

        user_nets = get_objects_for_user(
            user,
            ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
            any_perm=True
        )

        if network:
            if isinstance(network, unicode) or isinstance(network, str):
                network = Network.objects.get(network=network)

            if not user_nets.filter(network=network.network):
                raise ValidationError(
                    "You do not have access to assign host '%s' to the "
                    "network specified: %s." % (hostname, network)
                )

            try:
                network_address = Address.objects.filter(
                    Q(pool__in=user_pools) | Q(pool__isnull=True),
                    Q(leases__isnull=True) | Q(leases__abandoned=True) | Q(leases__ends__lte=timezone.now()),
                    network=network,
                    host__isnull=True,
                    reserved=False,
                ).order_by('address').first()

                if not network_address:
                    raise Address.DoesNotExist
                else:
                    address = network_address

            except AddrFormatError:
                raise ValidationError("The network '%s' is invalid." % network)
            except Address.DoesNotExist:
                raise ValidationError('There are no avaiable addresses for the network entered: %s' % network)

        elif ip_address:
            #Validate IP Address
            try:
                validate_ipv46_address(ip_address)
            except ValidationError:
                raise ValidationError('IP Address %s is invalid.  Enter a valid IPv4 or IPv6 address.' % ip_address)

            if ip_address in self.ip_addresses:
                raise ValidationError('IP address %s is already assigned to this host.' % ip_address)

            try:
                address = Address.objects.get(
                    Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
                    Q(leases__isnull=True) | Q(leases__abandoned=True) | Q(leases__ends__lte=timezone.now()),
                    Q(host__isnull=True) | Q(host=self),
                    address=ip_address,
                    reserved=False,
                )
            except AddrFormatError:
                raise ValidationError('There IP Address %s is not available.' % ip_address)
            except Address.DoesNotExist:
                raise ValidationError('There are no avaiable addresses for the IP entered: %s' % ip_address)
        else:
            raise ValidationError('A Network or IP Address must be given to assign this host an address.')

        # Make sure pool is clear on addresses we are assigning.
        address.pool_id = None
        address.host = self
        address.changed_by = user
        address.save()

        # Update A and PTR dns records
        self.add_dns_records(user, hostname, address)

        return address

    def add_dns_records(self, user, hostname, address):
        from openipam.dns.models import DnsRecord, DnsType

        if isinstance(address, str) or isinstance(address, unicode):
            from openipam.network.models import Address
            address = Address.objects.filter(address=address).first()

        # Delete Assocatiated PTR and A or AAAA records.
        self.dns_records.filter(
            Q(name=address.address.reverse_dns[:-1]) | Q(ip_content=address),
            dns_type__in=[DnsType.objects.PTR, DnsType.objects.A, DnsType.objects.AAAA]
        ).delete()

        # Add Associated PTR
        DnsRecord.objects.add_or_update_record(
            user=user,
            name=address.address.reverse_dns[:-1],
            content=hostname,
            dns_type=DnsType.objects.PTR,
            host=self
        )

        # Add Associated A or AAAA record
        DnsRecord.objects.add_or_update_record(
            user=user,
            name=hostname,
            content=address.address,
            dns_type=DnsType.objects.A if address.address.version == 4 else DnsType.objects.AAAA,
            host=self
        )

    def get_dns_records(self):
        from openipam.dns.models import DnsRecord

        addresses = self.addresses.all()
        a_record_names = (DnsRecord.objects
            .select_related('ip_content', 'host', 'dns_type')
            .filter(ip_content__in=addresses)
            .values_list('name')
        )
        dns_records = DnsRecord.objects.select_related('ip_content', 'host', 'dns_type').filter(
            Q(text_content__in=a_record_names) |
            Q(name__in=a_record_names) |
            Q(ip_content__in=addresses) |
            Q(host=self)
        ).order_by('dns_type__name')

        return dns_records

    def get_expire_days(self):
        if self.expires:
            delta = self.expires - timezone.now()
            return delta.days if delta.days > 0 else None
        else:
            return None

    def set_address_type(self):
        return self.address_type

    def set_expiration(self, expire_days):
        if isinstance(expire_days, int) or isinstance(expire_days, unicode) or isinstance(expire_days, str):
            expire_days = timedelta(int(expire_days))
        now = timezone.now()
        self.expires = datetime(now.year, now.month, now.day) + timedelta(1) + expire_days

    def set_mac_address(self, new_mac_address):
        if self.pk and self.pk.lower() != str(new_mac_address).lower():
            Host.objects.filter(mac=self.mac).update(mac=new_mac_address)
            self.pk = str(new_mac_address).lower()
        elif not self.pk:
            self.pk = str(new_mac_address).lower()

    # TODO: Clean this up, I dont like where this is at.
    def set_network_ip_or_pool(self, user=None, delete=False):
        if not user and self.user:
            user = self.user
        else:
            raise Exception('A User must be given to set a network or pool')

        # Set the pool if attached to model otherwise find it by address type
        pool = self.pool or getattr(self.address_type, 'pool', None)

        if delete:
            # Remove all pools
            self.pools.clear()
            # Remove all addresses
            self.addresses.release()

        # If we have a pool, this dynamic and we assign
        if pool:
            from openipam.network.models import Pool

            # Remove all addresses
            self.addresses.release()

            # TODO: Kill this later.
            host_pool_check = self.host_pools.all()
            if len(host_pool_check) > 1:
                self.pools.clear()

            host_pool = self.host_pools.filter(pool__name=pool).first()
            if host_pool:
                host_pool.changed_by = user
                host_pool.save()
            else:
                # Delete what is there and create a new one.
                self.pools.clear()
                # Assign new pool if it doesn't already exist
                self.host_pools.create(
                    host=self,
                    pool=Pool.objects.get(name=pool),
                    changed_by=user
                )

        # If we have an IP address, then assign that address to host
        else:
            # Remove all pools
            self.pools.clear()

            # Remove addresses if we are assinging a network
            # This implies that we want a new address even
            # if its in the same network
            current_addresses = self.ip_addresses
            if self.network or (self.ip_address and self.ip_address not in current_addresses):
                # Release the master IP to add another
                if self.master_ip_address:
                    self.addresses.filter(address=self.master_ip_address).release()

                # Add new master IP
                self.add_ip_address(
                    user=user,
                    ip_address=self.ip_address,
                    network=self.network,
                    hostname=self.hostname
                )
            else:
                a_record = self.get_dns_records().filter(
                    ip_content__address=self.master_ip_address,
                    name=self.hostname
                ).first()
                if a_record:
                    ptr_record = self.get_dns_records().filter(
                        text_content=self.hostname,
                        name=a_record.ip_content.address.reverse_dns[:-1]
                    )
                else:
                    ptr_record = None
                if not a_record or not ptr_record:
                    self.add_dns_records(user, self.hostname, self.master_ip_address)

    def remove_owners(self):
        users, groups = self.get_owners(ids_only=False)
        for user in users:
            remove_perm('is_owner_host', user, self)
        for group in groups:
            remove_perm('is_owner_host', group, self)

    def assign_owner(self, user_or_group):
        return assign_perm('is_owner_host', user_or_group, self)

    def save(self, *args, **kwargs):
        # Make sure hostname is lowercase
        self.hostname = self.hostname.lower()
        # Make sure mac is lowercase
        self.mac = str(self.mac).lower()

        super(Host, self).save(*args, **kwargs)

    def clean(self):
        from openipam.dns.models import DnsRecord
        from openipam.network.models import Address

        # Perform check to on hostname to not let users create a host
        if self.hostname and self.hostname != self.original_hostname:
            existing_hostname = Host.objects.filter(hostname=self.hostname).first()
            if existing_hostname:
                raise ValidationError("The hostname '%s' already exists." % (self.hostname))

            existing_dns_hostname = DnsRecord.objects.filter(name=self.hostname).first()
            if existing_dns_hostname:
                raise ValidationError('DNS Records already exist for this hostname: %s. '
                    ' Please contact an IPAM Administrator.' % (self.hostname))

        # Perform permission checks if user is attached to this instance
        # Domain permission checks if hostname has changed
        if self.hostname and self.hostname != self.original_hostname:
            domain_from_host = self.hostname.split('.')[1:]
            domain_from_host = '.'.join(domain_from_host)

            valid_domain = get_objects_for_user(
                self.user,
                ['dns.add_records_to_domain', 'dns.is_owner_domain', 'dns.change_domain'],
                any_perm=True
            ).filter(name=domain_from_host)
            if not valid_domain:
                raise ValidationError('Insufficient permissions to add hosts '
                                      'for domain: %s. Please contact an IPAM Administrator.' % domain_from_host)

        # Pool and Network permission checks
        # Check for pool assignment and perms
        if self.address_type and self.address_type.pool:
            valid_pools = get_objects_for_user(
                self.user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )
            if self.address_type.pool not in valid_pools:
                raise ValidationError('Insufficient permissions to add hosts to '
                                      'the assigned pool: %s. Please contact an IPAM Administrator.' % self.address_type.pool)

        # If network defined check for address assignment and perms
        if self.network:
            valid_network = get_objects_for_user(
                self.user,
                ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
                any_perm=True
            )
            if self.network.network not in [network.network for network in valid_network]:
                raise ValidationError('Insufficient permissions to add hosts to '
                  'the assigned network: %s. Please contact an IPAM Administrator.' % self.network.network)

        # If IP Address defined, check validity and perms
        if self.ip_address:
            ip_address = self.ip_address

            user_pools = get_objects_for_user(
                self.user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )
            user_nets = get_objects_for_user(
                self.user,
                ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
                any_perm=True
            )

            # Make sure this is valid.
            validate_ipv46_address(ip_address)
            address = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
                Q(leases__isnull=True) | Q(leases__abandoned=True) | Q(leases__ends__lte=timezone.now()),
                Q(host__isnull=True) | Q(host=self),
                address=ip_address,
                reserved=False
            )
            if not address:
                raise ValidationError('The IP Address is reserved, in use, or not allowed. '
                                      'Please contact an IPAM Administrator.')

    def reset_state(self):
        self._expire_days = None
        self._user_owners = None
        self._group_owners = None
        self._user = None

        self.ip_address = None
        self.pool = None
        self.network = None

        try:
            del self.ip_addresses
            del self.master_ip_address
            del self._pools_cache
            del self._addresses_cache
        except AttributeError:
            pass

    class Meta:
        db_table = 'hosts'
        permissions = (
            ('is_owner_host', 'Is owner'),
        )
        ordering = ('hostname',)


# TODO:  What is this?
# class Kvp(models.Model):
#     id = models.IntegerField()
#     key = models.TextField()
#     value = models.TextField()
#     class Meta:
#         db_table = 'kvp'


class MacOui(models.Model):
    oui = MACAddressField(primary_key=True)
    vendor = models.TextField()

    objects = NetManager()

    def __unicode__(self):
        return self.oui

    class Meta:
        db_table = 'mac_oui'


class Notification(models.Model):
    notification = models.DateField()
    hosts = models.ManyToManyField('Host', through='NotificationToHost', related_name='host_notifications')
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')

    def __unicode__(self):
        return '%s' % self.notification

    class Meta:
        db_table = 'notifications'


class NotificationToHost(models.Model):
    notification = models.ForeignKey('Notification', db_column='nid')
    host = models.ForeignKey('Host', db_column='mac')

    def __unicode__(self):
        return '%s %s' % (self.notification.notification, self.host.hostname)

    class Meta:
        db_table = 'notifications_to_hosts'


class StructuredAttributeValue(models.Model):
    attribute = models.ForeignKey('Attribute', db_column='aid', related_name='choices')
    value = models.TextField()
    is_default = models.BooleanField(default=False)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    def __unicode__(self):
        return self.value

    class Meta:
        db_table = 'structured_attribute_values'
        ordering = ('attribute__name', 'value',)


class StructuredAttributeToHost(models.Model):
    host = models.ForeignKey('Host', db_column='mac', related_name='structured_attributes')
    structured_attribute_value = models.ForeignKey('StructuredAttributeValue', db_column='avid')
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    def __unicode__(self):
        return '%s %s' % (self.host.hostname, self.structured_attribute_value)

    class Meta:
        db_table = 'structured_attributes_to_hosts'


# Host signals
pre_delete.connect(remove_obj_perms_connected_with_user, sender=Host)
