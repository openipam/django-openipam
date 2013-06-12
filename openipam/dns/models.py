from django.db import models
from django.core.exceptions import ValidationError


class DomainManager(models.Manager):
    pass


class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    master = models.CharField(max_length=128, blank=True)
    last_check = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(null=True, blank=True)
    account = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = DomainManager()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'domains'
        permissions = (
            ('is_owner', 'Is owner'),
            ('add_records_to', 'Can add records to'),
        )



class DnsRecord(models.Model):
    did = models.ForeignKey('Domain', db_column='did')
    tid = models.ForeignKey('DnsType', db_column='tid')
    vid = models.ForeignKey('DnsView', null=True, db_column='vid', blank=True)
    name = models.CharField(max_length=255)
    text_content = models.CharField(max_length=255, blank=True)
    ip_content = models.ForeignKey('network.Address', null=True, db_column='ip_content', blank=True, verbose_name='IP Content')
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return self.name

    def clean(self):
        if self.text_content and self.ip_content:
            raise ValidationError('`text_content` and `ip_content` cannot both have values.'
                                  '  Please choose one or the other')

    class Meta:
        db_table = 'dns_records'



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
    ttl = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dhcp_dns_records'


class DnsType(models.Model):
    name = models.CharField(max_length=16, blank=True)
    description = models.TextField(blank=True)
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dns_types'


class DnsView(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dns_views'


class Supermaster(models.Model):
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
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

