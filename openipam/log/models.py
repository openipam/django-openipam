from django.db import models
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from openipam.hosts.models import Host
from openipam.dns.models import DnsType
from openipam.network.models import Pool


class BaseLog(models.Model):
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        abstract = True


class HostLog(BaseLog):
    mac = models.TextField()  # This field type is a guess.
    hostname = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address_type = models.IntegerField(
        blank=True, null=True, db_column="address_type_id"
    )
    dhcp_group = models.IntegerField(null=True, blank=True)
    expires = models.DateTimeField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(
        "user.User",
        db_constraint=False,
        db_column="changed_by",
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return str(self.hostname)

    class Meta:
        managed = False
        db_table = "hosts_log"


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
        db_table = "pools_log"


class UserLog(BaseLog):
    id = models.IntegerField()
    username = models.CharField(max_length=50)
    source_id = models.IntegerField(db_column="source", blank=True, null=True)

    password = models.CharField(max_length=128, default="!")
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # is_ipamadmin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    @cached_property
    def source(self):
        return AuthSource.objects.get(id=self.source_id)

    @cached_property
    def is_ipamadmin(self):
        if self.is_superuser:
            return True
        else:
            group = Group.objects.get(name="ipam-admins")
            users = [user.username for user in group.user_set.all()]
            # assert False, users
            return True if self.username in users else False

    @cached_property
    def full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    class Meta:
        managed = False
        db_table = "users_log"


class EmailLog(models.Model):
    """
    Model to store all the outgoing emails.
    """

    when = models.DateTimeField(auto_now_add=True)
    to = models.EmailField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    # ok = models.BooleanField(null=False, default=True)

    def email_body(self):
        return mark_safe("<pre>%s</pre>" % self.body)

    class Meta:
        db_table = "email_log"


class DnsRecordLog(BaseLog):
    id = models.IntegerField()
    domain = models.IntegerField(db_column="did")
    type_id = models.IntegerField(db_column="tid")
    dns_view = models.IntegerField(db_column="vid")
    name = models.CharField(max_length=255)
    text_content = models.CharField(max_length=255, blank=True, null=True)
    ip_content = models.TextField(null=True, blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(
        "user.User",
        db_constraint=False,
        db_column="changed_by",
        on_delete=models.DO_NOTHING,
    )

    @cached_property
    def dns_type(self):
        return DnsType.objects.get(id=self.type_id)

    class Meta:
        managed = False
        db_table = "dns_records_log"


class AddressLog(BaseLog):
    address = models.GenericIPAddressField()
    mac = models.TextField(blank=True)  # This field type is a guess.
    pool = models.IntegerField()
    reserved = models.BooleanField()
    network = models.TextField(blank=True)  # This field type is a guess.
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(
        "user.User",
        db_constraint=False,
        db_column="changed_by",
        on_delete=models.DO_NOTHING,
    )

    @cached_property
    def pool_name(self):
        pool = Pool.objects.filter(id=self.pool).first()
        return pool

    @cached_property
    def host(self):
        try:
            host_obj = Host.objects.get(mac=self.mac)
        except ObjectDoesNotExist:
            host_obj = (
                HostLog.objects.filter(mac=self.mac).order_by("-trigger_id").first()
            )
        return host_obj

    def __str__(self):
        return str(self.address)

    class Meta:
        managed = False
        db_table = "addresses_log"


class LeaseLog(BaseLog):
    address = models.ForeignKey(
        "network.Address",
        db_constraint=False,
        db_column="address",
        on_delete=models.DO_NOTHING,
    )
    # address = models.GenericIPAddressField()
    mac = models.TextField(blank=True, null=True)  # This field type is a guess.
    abandoned = models.BooleanField()
    server = models.CharField(max_length=255, blank=True, null=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "leases_log"


class AuthSource(models.Model):
    name = models.CharField(unique=True, max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "auth_sources_log"
