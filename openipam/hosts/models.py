from django.db import models
from django.utils.timezone import utc
from django.core.exceptions import ValidationError
from netfields import InetAddressField, MACAddressField, NetManager
from guardian.managers import UserObjectPermissionManager
from guardian.shortcuts import get_objects_for_user
from openipam.hosts.validators import validate_hostname
from openipam.dns.models import Domain
from datetime import datetime


class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    structured = models.BooleanField()
    required = models.BooleanField()
    validation = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return self.name

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

    objects = NetManager()

    def __unicode__(self):
        return '%s %s' % (self.aid, self.name)

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
    expiration = models.TextField(blank=True) # This field type is a guess.
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')

    def __unicode__(self):
        return '%s days' % self.expiration.days

    class Meta:
        db_table = 'expiration_types'


class FreeformAttributeToHost(models.Model):
    mac = models.ForeignKey('Host', db_column='mac')
    aid = models.ForeignKey('Attribute', db_column='aid')
    value = models.TextField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return '%s %s %s' % (self.mac, self.aid, self.value)

    class Meta:
        db_table = 'freeform_attributes_to_hosts'


class GuestTicket(models.Model):
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
    address = InetAddressField(null=True, blank=True)
    stopstamp = models.DateTimeField(null=True, blank=True)

    objects = NetManager()

    def __unicode__(self):
        return '%s (%s - %s)' % (self.id, self.mac, self.address)

    class Meta:
        db_table = 'gul_recent_arp_byaddress'


class GulRecentArpBymac(models.Model):
    mac = MACAddressField(blank=True)
    address = InetAddressField(null=True, blank=True)
    stopstamp = models.DateTimeField(null=True, blank=True)

    objects = NetManager()

    def __unicode__(self):
        return '%s (%s - %s)' % (self.id, self.mac, self.address)

    class Meta:
        db_table = 'gul_recent_arp_bymac'


# class HostManager(NetManager, UserObjectPermissionManager):
#     pass


class Host(models.Model):
    mac = MACAddressField('Mac Address', primary_key=True)
    hostname = models.CharField(max_length=255, unique=True, validators=[validate_hostname])
    description = models.TextField(blank=True)
    address_type = models.ForeignKey('network.AddressType', blank=True, null=True)
    pools = models.ManyToManyField('network.Pool', through='network.HostToPool', related_name='pool_hosts')
    freeform_attributes = models.ManyToManyField('Attribute', through='FreeformAttributeToHost', related_name='freeform_hosts')
    structured_attributes = models.ManyToManyField('StructuredAttributeValue', through='StructuredAttributeToHost', related_name='structured_hosts')
    dhcp_group = models.ForeignKey('network.DhcpGroup', null=True, db_column='dhcp_group', blank=True, verbose_name='DHCP Group')
    expires = models.DateTimeField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('auth.User', db_column='changed_by')

    objects = NetManager()

    def __unicode__(self):
        return self.hostname

    def is_expired(self):
        return True if self.expires < datetime.utcnow().replace(tzinfo=utc) else False


    # Do hostname checks to make sure there is a FQDN
    # and that the user has permissions to add on that domain
    def clean_fields(self, exclude=None):
        super(Host, self).clean_fields(exclude)

        domain_names = self.hostname.split('.')
        domain_names.reverse()
        partial_domain = []
        domains_to_check = []
        for domain in domain_names:
            partial_domain.insert(0, domain)
            domains_to_check.append('.'.join(partial_domain))

        # Check user permissions
        domains = get_objects_for_user(self.changed_by, 'dns.add_within')
        # Check if domain exists
        domains = domains.filter(name__in=domains_to_check)
        if not domains:
            raise ValidationError({
                'hostname': ("No Domain found for host '%s'" % self.hostname,)
            })


    class Meta:
        db_table = 'hosts'
        permissions = (
            ('is_owner', 'Is owner'),
        )


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
    notification = models.TextField(blank=True)
    hosts = models.ManyToManyField('Host', through='NotificationToHost', related_name='host_notifications')
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')

    def __unicode__(self):
        return self.notification

    class Meta:
        db_table = 'notifications'


class NotificationToHost(models.Model):
    nid = models.ForeignKey('Notification', db_column='nid')
    mac = models.ForeignKey('Host', db_column='mac')

    def __unicode__(self):
        return '%s %s' % (self.nid, self.mac)

    class Meta:
        db_table = 'notifications_to_hosts'


class StructuredAttributeValue(models.Model):
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
    mac = models.ForeignKey('Host', db_column='mac')
    avid = models.ForeignKey('StructuredAttributeValue', db_column='avid')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return '%s %s' % (self.mac, self.avid)

    class Meta:
        db_table = 'structured_attributes_to_hosts'


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        "^netfields\.fields\.InetAddressField",
        "^netfields\.fields\.CidrAddressField",
        "^netfields\.fields\.MACAddressField",
    ])
except ImportError:
    pass


