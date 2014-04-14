from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import utc
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.functional import cached_property
from django.db.models.signals import post_save, pre_delete

from netfields import InetAddressField, MACAddressField, NetManager

from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms, \
    get_groups_with_perms, remove_perm, assign_perm

from openipam.hosts.signals import create_dns_record_for_static_host, delete_dns_record_for_static_host
from openipam.hosts.validators import validate_hostname
from openipam.hosts.managers import HostManager

from datetime import datetime


class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    structured = models.BooleanField()
    required = models.BooleanField()
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
    structured = models.BooleanField()
    required = models.BooleanField()
    mac = MACAddressField(blank=True, null=True)
    avid = models.IntegerField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    objects = NetManager()

    def __unicode__(self):
        return '%s %s' % (self.aid, self.name)

    class Meta:
        managed = False
        db_table = 'attributes_to_hosts'


class Disabled(models.Model):
    host = MACAddressField(primary_key=True, db_column='mac')
    reason = models.TextField(blank=True, null=True)
    disabled = models.DateTimeField(auto_now=True)
    disabled_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='disabled_by')

    def __unicode__(self):
        return self.host

    class Meta:
        db_table = 'disabled'
        verbose_name = 'Disabled Host'
        ordering = ('-disabled',)


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
        return '%s %s %s' % (self.host, self.attribute, self.value)

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

    class Meta:
        db_table = 'guest_tickets'


class GulRecentArpByaddress(models.Model):
    host = models.ForeignKey('Host', db_column='mac', related_name='ip_history', primary_key=True)
    address = InetAddressField()
    stopstamp = models.DateTimeField()

    objects = NetManager()

    def __unicode__(self):
        return '%s - %s' % (self.pk, self.address)

    class Meta:
        db_table = 'gul_recent_arp_byaddress'


class GulRecentArpBymac(models.Model):
    host = models.ForeignKey('Host', db_column='mac', related_name='mac_history', primary_key=True)
    address = InetAddressField()
    stopstamp = models.DateTimeField()

    objects = NetManager()

    def __unicode__(self):
        return '%s - %s' % (self.pk, self.address)

    class Meta:
        db_table = 'gul_recent_arp_bymac'


class Host(models.Model):
    mac = MACAddressField('Mac Address', primary_key=True)
    hostname = models.CharField(max_length=255, unique=True, validators=[validate_hostname], db_index=True)
    description = models.TextField(blank=True, null=True)
    address_type_id = models.ForeignKey('network.AddressType', blank=True, null=True, db_column='address_type_id')
    pools = models.ManyToManyField('network.Pool', through='network.HostToPool',
                                   related_name='pool_hosts',  blank=True, null=True)
    #freeform_attributes = models.ManyToManyField('Attribute', through='FreeformAttributeToHost',
    #                                             related_name='freeform_hosts',  blank=True, null=True)
    #structured_attributes = models.ManyToManyField('Attribute', through='StructuredAttributeToHost',
    #                                               related_name='structured_hosts',  blank=True, null=True)
    dhcp_group = models.ForeignKey('network.DhcpGroup', db_column='dhcp_group',
                                   verbose_name='DHCP Group', blank=True, null=True)
    expires = models.DateTimeField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    objects = HostManager()

    def __init__(self, *args, **kwargs):
        super(Host, self).__init__(*args, **kwargs)

        # Adding dummy fields that come from form or web service
        self.user = None
        self.ip_address = None
        self.ip_addresses = []
        self.network = None
        self.pool = None
        self.expire_days = self.get_expire_days()

    def __unicode__(self):
        return self.hostname

    @property
    def is_dynamic(self):
        return True if self.pools.all() else False

    @property
    def is_expired(self):
        return True if self.expires < timezone.now() else False

    @property
    def mac_is_disabled(self):
        return True if Disabled.objects.filter(host=self) else False

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

    def get_owners(self, ids_only=True):
        # users = self.user_permissions.filter(permission__codename='is_owner_host')
        # groups = self.group_permissions.filter(permission__codename='is_owner_host')

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

        if ids_only:
            users = [user.pk for user in users]
            groups = [group.pk for group in groups]

        return users, groups

    def get_ip_address(self):
        addresses = self.addresses.all().order_by('address')
        if addresses:
            return addresses[0]
        else:
            return None

    # def get_address_type(self):
    #     from openipam.network.models import AddressType, NetworkRange

    #     if self.address_type:
    #         return self.address_type
    #     elif not self.pk:
    #         self.address_type = None
    #     else:
    #         addresses = self.addresses.all()
    #         pools = self.pools.all()

    #         try:
    #             # if (len(addresses) + len(pools)) > 1:
    #             #     self.address_type = None
    #             # elif addresses:
    #             if addresses:
    #                 try:
    #                     ranges = NetworkRange.objects.filter(range__net_contained_or_equal=addresses[0].address)
    #                     if ranges:
    #                         self.address_type = AddressType.objects.get(ranges__range__in=ranges)
    #                     else:
    #                         raise AddressType.DoesNotExist
    #                 except AddressType.DoesNotExist:
    #                     self.address_type = AddressType.objects.get(is_default=True)
    #             elif pools:
    #                 self.address_type = AddressType.objects.get(pool=pools[0])
    #         except AddressType.DoesNotExist:
    #             self.address_type = None
    #         finally:
    #             pass
    #             #self.save()
    #     #assert False, self.address_type
    #     return self.address_type

    def get_dns_records(self):
        from openipam.dns.models import DnsRecord

        addresses = self.addresses.all()
        a_record_names = DnsRecord.objects.select_related().filter(ip_content__in=addresses).values_list('name')
        dns_records = DnsRecord.objects.select_related().filter(
            Q(text_content__in=a_record_names) | Q(name__in=a_record_names) | Q(ip_content__in=addresses)
        ).order_by('dns_type__name')

        return dns_records

    def get_expire_days(self):
        if self.expires:
            delta = self.expires - timezone.now()
            return delta.days if delta.days > 0 else None
        else:
            return None

    def set_expiration(self, expire_days):
        now = timezone.now()
        self.expires = datetime(now.year, now.month, now.day, 11, 59, 59).replace(tzinfo=utc) + expire_days

    def set_mac_address(self, new_mac_address):
        if self.pk and self.pk != new_mac_address:
            Host.objects.filter(mac=self.mac).update(mac=new_mac_address)

        self.pk = new_mac_address

    # TODO: Clean this up, I dont like where this is at.
    def set_network_ip_or_pool(self, user=None, delete=True):
        from openipam.network.models import Address, HostToPool

        if not user and self.user:
            user = self.user
        else:
            raise Exception('A User must be given to set a network or pool')

        # Set the pool if attached to model otherwise find it by address type
        if getattr(self, 'pool', None):
            pool = self.pool
        else:
            pool = self.address_type.pool

        if delete:
            # Remove all pools
            self.pools.clear()
            # Remove all addresses
            self.addresses.clear()

        # If we have a pool, this dynamic and we assign
        if pool:
            # Assign new pool if it doesn't already exist
            HostToPool.objects.get_or_create(
                host=self,
                pool=self.address_type.pool,
                changed_by=user
            )

        # If we have an IP address, then assign that address to host
        else:
            user_pools = get_objects_for_user(
                user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )

            if self.network:
                address = Address.objects.filter(
                    Q(pool__in=user_pools) | Q(pool__isnull=True),
                    network__network=self.network,
                    host__isnull=True,
                    reserved=False,
                ).order_by('address')

                if not address:
                    raise Address.DoesNotExist

                # Get only one
                address = address[0]
                # Make sure pool is clear.
                address.pool_id = None
                address.host = self
                address.changed_by = self.user
                address.save()

            elif self.ip_address or self.ip_addresses:
                if self.ip_address:
                    self.ip_addresses.append(self.ip_address)
                    self.ip_addresses = list(set(self.ip_addresses))

                for ip_address in self.ip_addresses:
                    address = Address.objects.get(
                        Q(pool__in=user_pools) | Q(pool__isnull=True),
                        address=ip_address,
                        host__isnull=True,
                        reserved=False,
                    )

                    # Make sure pool is clear.
                    address.pool_id = None
                    address.host = self
                    address.changed_by = self.user
                    address.save()
            else:
                raise Exception('A Network or IP Address must be given to assign this host.')

            # Make sure pool is clear.
            address.pool_id = None
            address.host = self
            address.changed_by = self.user
            address.save()

    def remove_owners(self):
        users, groups = self.get_owners(ids_only=False)
        for user in users:
            remove_perm('is_owner_host', user, self)
        for group in groups:
            remove_perm('is_owner_host', group, self)

    def assign_owner(self, user_or_group):
        return assign_perm('is_owner_host', user_or_group, self)

    def user_has_onwership(self, user):
        if user.is_ipamadmin:
            return True
        else:
            return True if self.mac in user.host_owner_permissions else False

    def save(self, *args, **kwargs):
        # Make sure hostname is lowercase
        self.hostname = self.hostname.lower()
        # Make sure mac is lowercase
        self.mac = str(self.mac).lower()

        super(Host, self).save(*args, **kwargs)

    def clean(self):

        # Perform permission checks if user is attached to this instance
        # and user is not an IPAM admin
        if self.user and not self.user.is_ipamadmin:

            # Domain permission checks
            if self.hostname:
                domain_from_host = self.hostname.split('.')[1:]
                domain_from_host = '.'.join(domain_from_host)

                valid_domain = get_objects_for_user(
                    self.user,
                    ['dns.add_records_to_domain', 'dns.is_owner_domain', 'dns.change_domain'],
                    #klass=Domain,
                    any_perm=True
                ).filter(name=domain_from_host)

                if not valid_domain:
                    raise ValidationError('You do not have sufficient permissions to add hosts '
                                          'for this domain. Please contact an IPAM Administrator.')

            # Pool and Network permission checks
            # Check for pool assignment and perms
            if self.address_type and self.address_type.pool:
                #assert False, self.address_type.pool
                valid_pools = get_objects_for_user(
                    self.user,
                    ['network.add_records_to_pool', 'network.change_pool'],
                    any_perm=True
                )
                if self.address_type.pool not in valid_pools:
                    raise ValidationError('You do not have sufficient permissions to add hosts to '
                                          'the assigned pool. Please contact an IPAM Administrator.')

            # Otherwise check for address assignment and perms
            elif self.network:
                valid_network = get_objects_for_user(
                    self.user,
                    ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
                    any_perm=True
                )
                if self.network not in [network.network for network in valid_network]:
                    raise ValidationError('You do not have sufficient permissions to add hosts to '
                      'the assigned network. Please contact an IPAM Administrator.')

    class Meta:
        db_table = 'hosts'
        permissions = (
            ('is_owner_host', 'Is owner'),
        )
        ordering = ('hostname',)


# class HostUserObjectPermission(UserObjectPermissionBase):
#     content_object = models.ForeignKey('Host', related_name='user_permissions')

#     class Meta:
#         verbose_name = 'Host User Permission'


# class HostGroupObjectPermission(GroupObjectPermissionBase):
#     content_object = models.ForeignKey('Host', related_name='group_permissions')

#     class Meta:
#         verbose_name = 'Host Group Permission'


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
        return '%s %s' % (self.nid, self.mac)

    class Meta:
        db_table = 'notifications_to_hosts'


class StructuredAttributeValue(models.Model):
    attribute = models.ForeignKey('Attribute', db_column='aid', related_name='choices')
    value = models.TextField()
    is_default = models.BooleanField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    def __unicode__(self):
        return self.value

    class Meta:
        db_table = 'structured_attribute_values'


class StructuredAttributeToHost(models.Model):
    host = models.ForeignKey('Host', db_column='mac', related_name='structured_attributes')
    structured_attribute_value = models.ForeignKey('StructuredAttributeValue', db_column='avid')
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    def __unicode__(self):
        return '%s %s' % (self.host, self.structured_attribute_value)

    class Meta:
        db_table = 'structured_attributes_to_hosts'


# Host signals
post_save.connect(create_dns_record_for_static_host, sender=Host)
pre_delete.connect(delete_dns_record_for_static_host, sender=Host)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        "^netfields\.fields\.InetAddressField",
        "^netfields\.fields\.CidrAddressField",
        "^netfields\.fields\.MACAddressField",
    ])
except ImportError:
    pass
