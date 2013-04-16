from django.db import models
from netfields import InetAddressField, MACAddressField


class Lease(models.Model):
    address = models.ForeignKey('Address', primary_key=True, db_column='address')
    mac = models.TextField(unique=True, blank=True) # This field type is a guess.
    abandoned = models.BooleanField()
    server = models.CharField(max_length=255, blank=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()
    class Meta:
        db_table = 'leases'


class Pool(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    allow_unknown = models.BooleanField()
    lease_time = models.IntegerField()
    dhcp_group = models.ForeignKey('DhcpGroup', null=True, db_column='dhcp_group', blank=True)
    class Meta:
        db_table = 'pools'


class DhcpGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'dhcp_groups'


class DhcpOption(models.Model):
    id = models.IntegerField(primary_key=True)
    size = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=255, unique=True, blank=True)
    option = models.CharField(max_length=255, unique=True, blank=True)
    comment = models.TextField(blank=True)
    class Meta:
        db_table = 'dhcp_options'


class DhcpOptionToDhcpGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    gid = models.ForeignKey('DhcpGroup', null=True, db_column='gid', blank=True)
    oid = models.ForeignKey('DhcpOption', null=True, db_column='oid', blank=True)
    value = models.TextField(blank=True) # This field type is a guess.
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'dhcp_options_to_dhcp_groups'


class HostToPool(models.Model):
    id = models.IntegerField(primary_key=True)
    mac = models.ForeignKey('host.Host', db_column='mac')
    pool = models.ForeignKey('Pool')
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'hosts_to_pools'


class SharedNetwork(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'shared_networks'


class Network(models.Model):
    network = InetAddressField(primary_key=True) # This field type is a guess.
    name = models.CharField(max_length=255, blank=True)
    gateway = InetAddressField(null=True, blank=True)
    description = models.TextField(blank=True)
    dhcp_group = models.ForeignKey('DhcpGroup', null=True, db_column='dhcp_group', blank=True)
    shared_network = models.ForeignKey('SharedNetwork', null=True, db_column='shared_network', blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'networks'


class Vlan(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=12)
    description = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'vlans'


class NetworkToVlan(models.Model):
    network = models.ForeignKey('Network', primary_key=True, db_column='network')
    vlan = models.ForeignKey('Vlan', db_column='vlan')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'networks_to_vlans'

class Address(models.Model):
    address = InetAddressField(primary_key=True)
    mac = models.ForeignKey('host.Host', null=True, db_column='mac', blank=True)
    pool = models.ForeignKey('Pool', null=True, db_column='pool', blank=True)
    reserved = models.BooleanField()
    network = models.ForeignKey('Network', db_column='network')
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'addresses'

