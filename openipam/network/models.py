from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from netfields import InetAddressField, MACAddressField, CidrAddressField, NetManager
from django.db.models.signals import m2m_changed


class Lease(models.Model):
    address = models.ForeignKey('Address', primary_key=True, db_column='address')
    mac = MACAddressField(unique=True, blank=True)
    abandoned = models.BooleanField()
    server = models.CharField(max_length=255, blank=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()

    objects = NetManager()

    def __unicode__(self):
        return self.address

    class Meta:
        db_table = 'leases'


class Pool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    allow_unknown = models.BooleanField()
    lease_time = models.IntegerField()
    dhcp_group = models.ForeignKey('DhcpGroup', null=True, db_column='dhcp_group', blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'pools'
        permissions = (
            ('add_records_to', 'Can add records to'),
        )


class DhcpGroup(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    dhcp_options = models.ManyToManyField('DhcpOption', through='DhcpOptionToDhcpGroup')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dhcp_groups'
        ordering = ('name',)


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
    value = models.TextField(blank=True) # This is really a bytea field, must stringify.
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
        return '%s' % self.network

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
    mac = models.ForeignKey('hosts.Host', null=True, db_column='mac', blank=True)
    pool = models.ForeignKey('Pool', null=True, db_column='pool', blank=True)
    reserved = models.BooleanField()
    network = models.ForeignKey('Network', db_column='network')
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = NetManager()

    def __unicode__(self):
        return self.address.strNormal()

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

    class Meta:
        db_table = 'addresstypes'

# Signal to make sure Address Types can only have a range OR pool.
def validate_address_type(sender, instance, action, **kwargs):
    if action == 'pre_add':
        if instance.pool:
            raise ValidationError(_('Address Types cannot have both a pool and a range.'))

m2m_changed.connect(validate_address_type, sender=AddressType.ranges.through)

