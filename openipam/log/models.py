from django.db import models
from django.utils.safestring import mark_safe

class BaseLog(models.Model):
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        abstract = True


class HostLog(BaseLog):
    mac = models.TextField() # This field type is a guess.
    hostname = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address_type = models.IntegerField(blank=True, null=True, db_column='address_type_id')
    dhcp_group = models.IntegerField(null=True, blank=True)
    expires = models.DateTimeField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_constraint=False, db_column='changed_by')

    class Meta:
        managed = False
        db_table = 'hosts_log'


class PoolLog(BaseLog):
    id = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    allow_unknown = models.BooleanField(default=False)
    lease_time = models.IntegerField()
    dhcp_group = models.IntegerField(null=True, blank=True)
    assignable = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'pools_log'


class UserLog(BaseLog):
    id = models.IntegerField()
    username = models.CharField(max_length=50)
    source = models.IntegerField()
    min_permissions = models.CharField(max_length=8)

    password = models.CharField(max_length=128, default='!')
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_ipamadmin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'users_log'


class EmailLog(models.Model):
    """
    Model to store all the outgoing emails.
    """
    when = models.DateTimeField(auto_now_add=True)
    to = models.EmailField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    #ok = models.BooleanField(null=False, default=True)

    def email_body(self):
        return mark_safe('<pre>%s</pre>' % self.body)

    class Meta:
        db_table = 'email_log'

class DnsRecordsLog(BaseLog):
    id = models.IntegerField()
    domain = models.IntegerField(db_column='did')
    dns_type = models.IntegerField(db_column='tid')
    dns_view = models.IntegerField(db_column='vid')
    name = models.CharField(max_length=255)
    text_content = models.CharField(max_length=255, blank=True, null=True)
    ip_content = models.TextField(null=True, blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('user.User', db_constraint=False, db_column='changed_by')

    class Meta:
        managed = False
        db_table = 'dns_records_log'


# class AddressLog(BaseLog):
#     address = models.GenericIPAddressField()
#     mac = models.TextField(blank=True) # This field type is a guess.
#     pool = models.IntegerField(null=True, blank=True)
#     reserved = models.BooleanField()
#     network = models.TextField(blank=True) # This field type is a guess.
#     changed = models.DateTimeField(null=True, blank=True)
#     changed_by = models.IntegerField(null=True, blank=True)

#     class Meta:
#         managed = False
#         db_table = 'addresses_log'


# class DomainLog(BaseLog):
#     id = models.IntegerField()
#     name = models.CharField(max_length=255)
#     master = models.CharField(max_length=128, blank=True)
#     last_check = models.IntegerField(null=True, blank=True)
#     type = models.CharField(max_length=6)
#     notified_serial = models.IntegerField(null=True, blank=True)
#     account = models.CharField(max_length=40, blank=True)
#     description = models.TextField(blank=True)
#     changed = models.DateTimeField(null=True, blank=True)
#     changed_by = models.IntegerField()

#     class Meta:
#         managed = False
#         db_table = 'domains_log'
