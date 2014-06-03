from django.db import models


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
    changed_by = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'hosts_log'


class PoolLog(BaseLog):
    id = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    allow_unknown = models.BooleanField()
    lease_time = models.IntegerField()
    dhcp_group = models.IntegerField(null=True, blank=True)
    assignable = models.BooleanField()

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
