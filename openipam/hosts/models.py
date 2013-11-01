from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from netfields import InetAddressField, MACAddressField, NetManager

from guardian.managers import UserObjectPermissionManager
from guardian.models import UserObjectPermission, GroupObjectPermission, \
    UserObjectPermissionBase, GroupObjectPermissionBase
from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms, \
    get_groups_with_perms, remove_perm, assign_perm

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
    mac = MACAddressField(primary_key=True)
    reason = models.TextField(blank=True, null=True)
    disabled = models.DateTimeField(auto_now=True)
    disabled_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='disabled_by')

    def __unicode__(self):
        return self.mac

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
    mac = models.ForeignKey('Host', db_column='mac', related_name='freeform_attributes')
    attribute = models.ForeignKey('Attribute', db_column='aid')
    value = models.TextField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    def __unicode__(self):
        return '%s %s %s' % (self.mac, self.aid, self.value)

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
    mac = MACAddressField(primary_key=True)
    address = InetAddressField()
    stopstamp = models.DateTimeField()

    objects = NetManager()

    def __unicode__(self):
        return '%s - %s' % (self.mac, self.address)

    class Meta:
        db_table = 'gul_recent_arp_byaddress'


class GulRecentArpBymac(models.Model):
    mac = MACAddressField(primary_key=True)
    address = InetAddressField()
    stopstamp = models.DateTimeField()

    objects = NetManager()

    def __unicode__(self):
        return '%s - %s' % (self.mac, self.address)

    class Meta:
        db_table = 'gul_recent_arp_bymac'


class Host(models.Model):
    mac = MACAddressField('Mac Address', primary_key=True)
    hostname = models.CharField(max_length=255, unique=True, validators=[validate_hostname])
    description = models.TextField(blank=True, null=True)
    address_type = models.ForeignKey('network.AddressType', blank=True, null=True)
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
    #gul_recent_arp_bymac = GulRecentArpBymac.objects.all()
    #gul_recent_arp_byaddress = GulRecentArpByaddress.objects.all()

    @property
    def is_dynamic(self):
        return True if self.pools.all() else False

    @property
    def is_expired(self):
        return True if self.expires < timezone.now() else False

    @property
    def mac_is_disabled(self):
        return True if Disabled.objects.filter(mac=self.mac) else False

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
    def static_ip_last_seen(self):
        gul_ip = GulRecentArpByaddress.objects.filter(mac=self.mac).order_by('-stopstamp')

        #ul_ip = filter(lambda x: x.mac == self.mac, self.gul_recent_arp_byaddress)

        if gul_ip:
            return gul_ip[0].stopstamp
        else:
            return None

    @property
    def owners(self):
        user_list = []
        group_list = []

        users = get_users_with_perms(self, attach_perms=True)
        for user, perm in users.iteritems():
            if 'is_owner' in perm:
                user_list.append(user)

        groups = get_groups_with_perms(self, attach_perms=True)
        for group, perm in groups.iteritems():
            if 'is_owner' in perm:
                group_list.append(group)

        return (user_list, group_list)

    def get_ip_address(self):
        addresses = self.addresses.all()
        if addresses:
            return addresses[0]
        else:
            return None

    def get_address_type(self):
        from openipam.network.models import AddressType

        if self.address_type:
            return self.address_type
        else:
            addresses = self.addresses.all()
            pools = self.pools.all()

            try:
                if (len(addresses) + len(pools)) > 1:
                    self.address_type = None
                elif addresses:
                    try:
                        self.address_type = AddressType.objects.get(ranges__range__net_contained_or_equal=addresses[0])
                    except AddressType.DoesNotExist:
                        self.address_type = AddressType.objects.get(is_default=True)
                elif pools:
                    self.address_type = AddressType.objects.get(pool=pools[0])
            except AddressType.DoesNotExist:
                self.address_type = None
            finally:
                self.save()

        return self.address_type

    def remove_owners(self):
        owners = self.owners
        for user in owners[0]:
            remove_perm('is_owner_host', user, self)
        for group in owners[0]:
            remove_perm('is_owner_host', group, self)

    def assign_owner(self, user_or_group):
        return assign_perm('is_owner_host', user_or_group, self)

    def dns_records(self):
        from openipam.dns.models import DnsRecord

        addresses = self.addresses.all()
        a_record_names = DnsRecord.objects.select_related().filter(ip_content__in=addresses).values_list('name')
        dns_records = DnsRecord.objects.select_related().filter(
            Q(text_content__in=a_record_names) | Q(name__in=a_record_names) | Q(ip_content__in=addresses)
        ).order_by('dns_type__name')

        return dns_records

    def __unicode__(self):
        return self.hostname

    def clean(self):
        # Make sure hostname is lowercase
        self.hostname = self.hostname.lower()

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
        if hasattr(self, 'changed_by'):
            try:
                domains = get_objects_for_user(self.changed_by, 'dns.add_within')
            except ContentType.DoesNotExist:
                return

            # Check if domain exists
            domains = domains.filter(name__in=domains_to_check)
            if not domains:
                raise ValidationError({
                    'hostname': ("No Domain found for host '%s'" % self.hostname,)
                })

    class Meta:
        db_table = 'hosts'
        permissions = (
            ('is_owner_host', 'Is owner'),
        )
        ordering = ('hostname',)


class HostUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey('Host', related_name='user_permissions')

    class Meta:
        verbose_name = 'Host User Permission'


class HostGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey('Host', related_name='group_permissions')

    class Meta:
        verbose_name = 'Host Group Permission'


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
    attribute = models.ForeignKey('Attribute', db_column='aid')
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
