from django.db import models
from netfields import InetAddressField, MACAddressField


class Attribute(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    structured = models.BooleanField()
    required = models.BooleanField()
    validation = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')
    class Meta:
        db_table = 'attributes'


class AttributeToHost(models.Model):
    aid = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    structured = models.BooleanField()
    required = models.BooleanField()
    mac = MACAddressField(blank=True)
    avid = models.IntegerField(null=True, blank=True)
    value = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'attributes_to_hosts'



class Disabled(models.Model):
    mac = MACAddressField(primary_key=True)
    reason = models.TextField(blank=True)
    disabled = models.DateTimeField(null=True, blank=True)
    disabled_by = models.ForeignKey('user.User', db_column='disabled_by')

    def __unicode__(self):
        return self.mac

    class Meta:
        db_table = 'disabled'
        verbose_name = 'Disabled Host'


class ExpirationType(models.Model):
    id = models.IntegerField(primary_key=True)
    expiration = models.TextField(blank=True) # This field type is a guess.
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')
    class Meta:
        db_table = 'expiration_types'


class FreeformAttributeToHost(models.Model):
    id = models.IntegerField(primary_key=True)
    mac = models.ForeignKey('Host', db_column='mac')
    aid = models.ForeignKey('Attribute', db_column='aid')
    value = models.TextField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')
    class Meta:
        db_table = 'freeform_attributes_to_hosts'


class GuestTicket(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.ForeignKey('user.User', db_column='uid', verbose_name='Group')
    ticket = models.CharField(max_length=255, unique=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.ticket

    class Meta:
        db_table = 'guest_tickets'


class GulRecentArpByaddress(models.Model):
    mac = MACAddressField(blank=True)
    address = models.GenericIPAddressField(null=True, blank=True)
    stopstamp = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'gul_recent_arp_byaddress'


class GulRecentArpBymac(models.Model):
    mac = MACAddressField(blank=True)
    address = models.GenericIPAddressField(null=True, blank=True)
    stopstamp = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'gul_recent_arp_bymac'


class Host(models.Model):
    mac = MACAddressField(primary_key=True)
    hostname = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    dhcp_group = models.ForeignKey('network.DhcpGroup', null=True, db_column='dhcp_group', blank=True)
    expires = models.DateTimeField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return self.hostname

    class Meta:
        db_table = 'hosts'
        verbose_name = 'Active Host'


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
    class Meta:
        db_table = 'mac_oui'


class Notification(models.Model):
    id = models.IntegerField(primary_key=True)
    notification = models.TextField(blank=True)
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')

    class Meta:
        db_table = 'notifications'


class NotificationToHost(models.Model):
    id = models.IntegerField(primary_key=True)
    nid = models.ForeignKey('Notification', db_column='nid')
    mac = models.ForeignKey('Host', db_column='mac')
    class Meta:
        db_table = 'notifications_to_hosts'


class StructuredAttributeValue(models.Model):
    id = models.IntegerField(primary_key=True)
    aid = models.ForeignKey('Attribute', db_column='aid')
    value = models.TextField()
    is_default = models.BooleanField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return self.value

    class Meta:
        db_table = 'structured_attribute_values'


class StructuredAttributeToHost(models.Model):
    id = models.IntegerField(primary_key=True)
    mac = models.ForeignKey('Host', db_column='mac')
    avid = models.ForeignKey('StructuredAttributeValue', db_column='avid')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')
    class Meta:
        db_table = 'structured_attributes_to_hosts'






## User Models
# TODO: Delete eventually

