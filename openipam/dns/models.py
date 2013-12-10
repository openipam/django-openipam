from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address, validate_ipv6_address

from openipam.dns.managers import DnsManager, DomainManager
from openipam.dns.validators import validate_fqdn, validate_soa_content, \
    validate_srv_content, validate_sshfp_content

from guardian.models import UserObjectPermissionBase, GroupObjectPermissionBase

from netaddr.core import AddrFormatError

import re
import operator


class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    master = models.CharField(max_length=128, blank=True, null=True, default=None)
    last_check = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(blank=True, null=True)
    account = models.CharField(max_length=40, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = DomainManager()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'domains'
        permissions = (
            ('is_owner_domain', 'Is owner'),
            ('add_records_to_domain', 'Can add records to'),
        )


class DomainUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey('Domain', related_name='user_permissions')

    class Meta:
        verbose_name = 'Domain User Permission'


class DomainGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey('Domain', related_name='group_permissions')

    class Meta:
        verbose_name = 'Domain Group Permission'


class DnsRecord(models.Model):
    domain = models.ForeignKey('Domain', db_column='did', verbose_name='Domain')
    dns_type = models.ForeignKey('DnsType', db_column='tid', verbose_name='Type')
    dns_view = models.ForeignKey('DnsView', db_column='vid', verbose_name='View', blank=True, null=True)
    name = models.CharField(max_length=255)
    text_content = models.CharField(max_length=255, blank=True, null=True)
    ip_content = models.ForeignKey('network.Address', db_column='ip_content', verbose_name='IP Content', blank=True, null=True)
    ttl = models.IntegerField(default=86400, blank=True, null=True)
    priority = models.IntegerField(verbose_name='Priority', blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = DnsManager()

    def __unicode__(self):
        return self.name

    def clean(self):
        # Make sure these are saved as NULL to db.
        if not self.text_content:
            self.text_content = None
        if not self.ip_content:
            self.ip_content = None

        # Make sure we have text or ip content
        if not self.text_content and not self.ip_content:
            raise ValidationError('Either Text Content or IP Content must exist for %s.' % self.name)

        # But we cannot have both text and ip content
        if self.text_content and self.ip_content:
            raise ValidationError('Text Content and IP Content cannot both exist for %s.' % self.name)

    def clean_fields(self, exclude=None):
        errors = {}

        try:
            super(DnsRecord, self).clean_fields(exclude)
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        # Clean the name
        try:
            self.clean_name()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        # Clean the domain
        try:
            self.clean_domain()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        # Clean the text_content
        try:
            self.clean_text_content()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        # Clean the priority
        try:
            self.clean_priority()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        # Clean the dns_type
        try:
            self.clean_dns_type()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    def clean_name(self):
        # Make sure name is lowercase
        self.name = self.name.lower()

        # Clean name if PTR record
        if self.dns_type.name == 'PTR' and self.domain:
            if 'in-addr.arpa' not in self.name and 'ip6.arpa' not in self.name:
                raise ValidationError({'name': ['Invalid name for PTR: %s' % self.name]})

    def clean_domain(self):
        if self.domain.type == 'SLAVE':
            raise ValidationError({'name': ['Cannot create name %s: not authoritative for domain' % self.name]})

        names = self.name.split('.')[1:]
        names_list = []
        while names:
            names_list.append(Q(name='.'.join(names)))
            names.pop(0)

        domains = Domain.objects.filter(reduce(operator.or_, names_list))
        domains = domains.extra(select={'length': 'Length(name)'}).order_by('-length')

        if domains:
            self.domain = domains[0]
        else:
            raise ValidationError({'name': 'Invalid domain name: %s' % self.name})

    def clean_text_content(self):
        errors_list = []

        # Validate text content based on dns type
        # TODO: more of these need to be added
        if self.text_content:
            fqdn = "([0-9A-Za-z]+\.[0-9A-Za-z]+|[0-9A-Za-z]+[\-0-9A-Za-z\.]*[0-9A-Za-z])"

            if self.dns_type.name in ['NS', 'CNAME', 'PTR', 'MX']:
                re_fqdn = re.compile("^"+fqdn+"$")
                if not re_fqdn.search(self.text_content):
                    errors_list.append('Invalid Name: %s' % self.text_content)
            elif self.dns_type.name == 'SOA':
                validate_soa_content(self.text_content)
                re_soa = re.compile('^%s [A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4} \d+ \d+ \d+ \d+ \d+$' % fqdn)
                if not re_soa.search(self.text_content):
                    errors_list.append('Invalid SOA Content: %s' % self.text_content)
            elif self.dns_type.name == 'SRV':
                re_srv = re.compile('^(\d+ \d+ %s)$' % fqdn)
                if not re_srv.search(self.text_content):
                    errors_list.append('Invalid SRV Content: %s' % self.text_content)
            elif self.dns_type.name == 'SSHFP':
                if not re.match('^[12] 1 [0-9A-F]{40}', self.text_content):
                    errors_list.append('Invalid SSHFP Content: %s' % self.text_content)

            try:
                if self.dns_type.name == 'A':
                    validate_ipv4_address(self.text_content)
                elif self.dns_type.name == 'AAAA':
                    validate_ipv6_address(self.text_content)
            except ValidationError as e:
                errors_list += e.error_list

        if errors_list:
            raise ValidationError({'text_content': errors_list})

    def clean_priority(self):
        # Priority must exist for MX and SRV records
        if self.dns_type.name in ['MX', 'SRV'] and not self.priority:
            raise ValidationError({'priority': ['Prority must exist for MX and SRV records.']})

    def clean_dns_type(self):
        error_list = []

        # Text content cannot exist for A records and IP must exist for A records
        if self.dns_type_id in ['A', 'AAAA']:
            if self.text_content:
                error_list.append('Text Content must not exist for A records.')
            if not self.ip_content:
                error_list.append('IP Content must exist for A records.')

        # Name and text content cannot be the same if its not an CNAME
        if self.dns_type.name != 'CNAME':
            if self.name == self.text_content:
                error_list.append('Name and Text Content cannot match for records order than CNAME.')

        if self.dns_type.name == 'CNAME':
            records = DnsRecord.objects.filter(name=self.name, dns_view=self.dns_view)
            if records:
                error_list.append('Trying to create CNAME record while other records exist: %s' % records[0].name)
        else: # not CNAME
            records = DnsRecord.objects.filter(name=self.name, dns_view=self.dns_view, dns_type_id=5)
            if records:
                error_list.append('Trying to create record while CNAME record exists:  %s' % records[0].name)

        if error_list:
            raise ValidationError({'dns_type': error_list})

    def set_priority(self):
        """
        Checks for priority and sets it if it exists
        """
        # Make sure that priority was set, or set it if they passed it
        match = None
        if self.dns_type.name != 'A':
            if self.dns_type.name == 'MX': # MX
                match = re.compile('^([0-9]{1,2}) (.*)$').search(self.text_content)
            elif self.dns_type.name == 'SRV': # SRV
                match = re.compile('^([0-9]{1,2}) (\d+ \d+ .*)$').search(self.text_content)

            if match:
                # We have priority in the content
                self.priority = match.group(1)
                self.text_content = match.group(2)

    def user_has_ownership(self, user):
        user.attach_permissions()

        if user.is_ipamadmin:
            return True
        elif self.ip_content and self.ip_content.host.mac in user.host_owner_permissions:
            return True
        elif self.domain.name in user.domain_owner_permissions:
            return True

        return False

    class Meta:
        db_table = 'dns_records'
        ordering = ('dns_type', 'name')
        verbose_name = 'DNS Record'


class DnsRecordMunged(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'dns_records_munged'


class DhcpDnsRecord(models.Model):
    did = models.ForeignKey('Domain', db_column='did')
    name = models.ForeignKey('hosts.Host', unique=True, db_column='name')
    ip_content = models.ForeignKey('network.Address', null=True, db_column='ip_content', blank=True)
    ttl = models.IntegerField(default=-1, blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dhcp_dns_records'


class DnsType(models.Model):
    name = models.CharField(max_length=16, blank=True, unique=True)
    description = models.TextField(blank=True, null=True)
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')

    def __unicode__(self):
        return '%s' % self.name

    @property
    def is_a_record(self):
        return True if self.name in ['A', 'AAAA'] else False

    class Meta:
        db_table = 'dns_types'
        permissions = (
            ('add_records_to_dnstype', 'Can add records to'),
        )
        ordering = ('name',)
        verbose_name = 'DNS Type'


class DnsTypeUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey('DnsType', related_name='user_permissions')


class DnsTypeGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey('DnsType', related_name='group_permissions')


class DnsView(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        db_table = 'dns_views'


class Supermaster(models.Model):
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True, null=True, default=None)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return self.ip

    class Meta:
        db_table = 'supermasters'


class PdnsZoneXfer(models.Model):
    domain = models.ForeignKey('Domain')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    content = models.CharField(max_length=255)
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'pdns_zone_xfer'


class Record(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.id, self.name)

    class Meta:
        managed = False
        db_table = 'records'


class RecordMunged(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.id, self.name)

    class Meta:
        managed = False
        db_table = 'records_munged'

