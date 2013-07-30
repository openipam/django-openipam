from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from netfields import InetAddressField, MACAddressField, CidrAddressField, NetManager
from django.db.models.signals import m2m_changed, post_save

from openipam.network.managers import LeaseManager, PoolManager, AddressManager


class Lease(models.Model):
    address = models.ForeignKey('Address', primary_key=True, db_column='address')
    mac = MACAddressField(unique=True, blank=True)
    abandoned = models.BooleanField()
    server = models.CharField(max_length=255, blank=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()

    objects = LeaseManager()

    def __unicode__(self):
        return self.address

    class Meta:
        db_table = 'leases'


class Pool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    allow_unknown = models.BooleanField()
    lease_time = models.IntegerField()
    assignable = models.BooleanField()
    dhcp_group = models.ForeignKey('DhcpGroup', null=True, db_column='dhcp_group', blank=True)

    objects = PoolManager()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'pools'
        permissions = (
            ('add_records_to', 'Can add records to'),
        )


class DefaultPool(models.Model):
    pool = models.ForeignKey('Pool', related_name='pool_defaults', blank=True, null=True)
    cidr = CidrAddressField(unique=True)

    objects = NetManager()

    def __unicode__(self):
        return '%s - %s' % (self.pool, self.cidr)

    class Meta:
        db_table = 'default_pools'


class DhcpGroupManager(models.Manager):

    def get_query_set(self):
        qs = super(DhcpGroupManager, self).get_query_set()
        qs = qs.extra(select={'lname': 'lower(name)'}).order_by('lname')

        return qs


class DhcpGroup(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    dhcp_options = models.ManyToManyField('DhcpOption', through='DhcpOptionToDhcpGroup')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = DhcpGroupManager()

    def __unicode__(self):
        return '%s -- %s' % (self.name, self.description)

    class Meta:
        db_table = 'dhcp_groups'


class DhcpOption(models.Model):
    size = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=255, unique=True, blank=True)
    option = models.CharField(max_length=255, unique=True, blank=True)
    comment = models.TextField(blank=True)

    def __unicode__(self):
        return '%s_%s' % (self.id, self.name)

    class Meta:
        db_table = 'dhcp_options'


class DhcpOptionToDhcpGroup(models.Model):
    gid = models.ForeignKey('DhcpGroup', null=True, db_column='gid', blank=True, related_name='option_values')
    oid = models.ForeignKey('DhcpOption', null=True, db_column='oid', blank=True, related_name='group_values')
    value = models.TextField(blank=True)    # This is really a bytea field, must stringify.
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return '%s:%s=%r' % (self.gid, self.oid, str(self.value))

    class Meta:
        db_table = 'dhcp_options_to_dhcp_groups'


class HostToPool(models.Model):
    mac = models.ForeignKey('hosts.Host', db_column='mac')
    pool = models.ForeignKey('Pool')
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return '%s %s' % (self.mac, self.pool)

    class Meta:
        db_table = 'hosts_to_pools'


class SharedNetwork(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'shared_networks'


class Network(models.Model):
    network = CidrAddressField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    gateway = InetAddressField(null=True, blank=True)
    description = models.TextField(blank=True)
    vlans = models.ManyToManyField('Vlan', through='NetworkToVlan', related_name='vlan_networks')
    dhcp_group = models.ForeignKey('DhcpGroup', null=True, db_column='dhcp_group', blank=True)
    shared_network = models.ForeignKey('SharedNetwork', null=True, db_column='shared_network', blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = NetManager()

    def __unicode__(self):
        return '%s -- %s' % (self.network, self.name)

    class Meta:
        db_table = 'networks'
        permissions = (
            ('is_owner', 'Is owner'),
            ('add_records_to', 'Can add records to'),
        )


class NetworkRange(models.Model):
    range = CidrAddressField(unique=True)

    objects = NetManager()

    def __unicode__(self):
        return '%s' % self.range

    class Meta:
        db_table = 'network_ranges'


class Vlan(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=12)
    description = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return '%s %s' % (self.id, self.name)

    class Meta:
        db_table = 'vlans'


class NetworkToVlan(models.Model):
    network = models.ForeignKey('Network', primary_key=True, db_column='network')
    vlan = models.ForeignKey('Vlan', db_column='vlan')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return '%s %s' % (self.network, self.vlan)

    class Meta:
        db_table = 'networks_to_vlans'


class Address(models.Model):
    address = InetAddressField(primary_key=True)
    mac = models.ForeignKey('hosts.Host',db_column='mac', blank=True, null=True, related_name='addresses')
    pool = models.ForeignKey('Pool', db_column='pool', blank=True, null=True)
    reserved = models.BooleanField()
    network = models.ForeignKey('Network', db_column='network')
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = AddressManager()

    def __unicode__(self):
        return unicode(self.address)

    def clean(self):
        if self.mac and self.pool:
            raise ValidationError('MAC and Pool cannot both be defined.  Choose one or the other.')
        elif (self.mac or self.pool) and self.reserved:
            raise ValidationError('If a MAC or Pool are defined, reserved must be false.')

    def release(self, pool=False):
        from openipam.dns.models import DnsRecord

        # Get default pool if false
        if pool is False:
            pool = (DefaultPool.objects
                .filter(cidr__net_contains_or_equals=self.address)
                .extra(select={'masklen': "masklen(cidr)"}, order_by=['masklen']))
        # Assume an int of not Model
        elif not isinstance(pool, models.Model):
            pool = DefaultPool.objects.get(pk=pool)

        # Delete dns PTR records
        DnsRecord.objects.filter(name=self.address.reverse_dns).delete()
        # Delete dns A records
        DnsRecord.objects.filter(address=self).delete()

        # Set new pool and save
        self.pool = pool
        self.save()

    # Signal to delete leases when an address is changed, if MAC is set to None.
    @staticmethod
    def release_leases(sender, instance, action, **kwargs):
        if not instance.mac:
            Lease.objects.filter(address=instance).delete()

    class Meta:
        db_table = 'addresses'


class AddressType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ranges = models.ManyToManyField('NetworkRange', blank=True, null=True)
    pool = models.ForeignKey('Pool', blank=True, null=True)
    is_default = models.BooleanField()

    def __unicode__(self):
        return self.name

    def clean(self):
        if self.is_default and AddressType.objects.filter(is_default=True):
            raise ValidationError(_('There can only be one default Address Type'))

    # Signal to make sure Address Types can only have a range OR pool.
    @staticmethod
    def validate_address_type(sender, instance, action, **kwargs):
        if action == 'pre_add':
            if instance.pool:
                raise ValidationError(_('Address Types cannot have both a pool and a range.'))

    class Meta:
        db_table = 'addresstypes'
        ordering = ('name',)


# Register Signals
m2m_changed.connect(AddressType.validate_address_type, sender=AddressType.ranges.through)
post_save.connect(Address.release_leases, sender=Address)
