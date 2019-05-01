from django.db import models


class AddressesLog(models.Model):
    address = models.GenericIPAddressField()
    mac = models.TextField(blank=True)  # This field type is a guess.
    pool = models.IntegerField(null=True, blank=True)
    reserved = models.BooleanField(null=True, blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)
    network = models.TextField(blank=True)  # This field type is a guess.
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "addresses_log"


class AttributesLog(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    structured = models.BooleanField()
    required = models.BooleanField()
    validation = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "attributes_log"


class AttributesToHostsLog(models.Model):
    id = models.IntegerField()
    aid = models.IntegerField(null=True, blank=True)
    text_value = models.TextField(blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "attributes_to_hosts_log"


class AuthSourcesLog(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=-1, blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "auth_sources_log"


class DhcpDnsRecordsLog(models.Model):
    id = models.IntegerField()
    did = models.IntegerField()
    name = models.CharField(max_length=255)
    ip_content = models.GenericIPAddressField(null=True, blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "dhcp_dns_records_log"


class DhcpGroupsLog(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "dhcp_groups_log"


class DhcpOptionsLog(models.Model):
    id = models.IntegerField()
    size = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=255, blank=True)
    option = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "dhcp_options_log"


class DhcpOptionsToDhcpGroupsLog(models.Model):
    id = models.IntegerField()
    gid = models.IntegerField(null=True, blank=True)
    oid = models.IntegerField(null=True, blank=True)
    value = models.TextField(blank=True)  # This field type is a guess.
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "dhcp_options_to_dhcp_groups_log"


class DisabledLog(models.Model):
    mac = models.TextField()  # This field type is a guess.
    reason = models.TextField(blank=True)
    disabled = models.DateTimeField(null=True, blank=True)
    disabled_by = models.IntegerField(null=True, blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "disabled_log"


class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user = models.ForeignKey(AuthUser)
    content_type = models.ForeignKey("DjangoContentType", null=True, blank=True)
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DnsRecordsLog(models.Model):
    id = models.IntegerField()
    did = models.IntegerField()
    tid = models.IntegerField()
    vid = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    text_content = models.CharField(max_length=255, blank=True)
    ip_content = models.GenericIPAddressField(null=True, blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "dns_records_log"


class DnsTypesLog(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=16, blank=True)
    description = models.TextField(blank=True)
    min_permissions = models.TextField()  # This field type is a guess.
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "dns_types_log"


class DnsViewsLog(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "dns_views_log"


class DomainsLog(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=255)
    master = models.CharField(max_length=128, blank=True)
    last_check = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(null=True, blank=True)
    account = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "domains_log"


class DomainsToGroupsLog(models.Model):
    id = models.IntegerField()
    did = models.IntegerField()
    gid = models.IntegerField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "domains_to_groups_log"


class ExpirationTypesLog(models.Model):
    id = models.IntegerField()
    expiration = models.TextField(blank=True)  # This field type is a guess.
    min_permissions = models.TextField()  # This field type is a guess.
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "expiration_types_log"


class FreeformAttributesToHostsLog(models.Model):
    id = models.IntegerField()
    mac = models.TextField()  # This field type is a guess.
    aid = models.IntegerField()
    value = models.TextField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "freeform_attributes_to_hosts_log"


class GroupsLog(models.Model):
    id = models.IntegerField()
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "groups_log"


class GuestTicketsLog(models.Model):
    id = models.IntegerField()
    uid = models.IntegerField()
    ticket = models.CharField(max_length=255)
    starts = models.DateTimeField()
    ends = models.DateTimeField()
    description = models.TextField(blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "guest_tickets_log"


class HostsLog(models.Model):
    mac = models.TextField()  # This field type is a guess.
    hostname = models.CharField(max_length=-1)
    description = models.TextField(blank=True)
    dhcp_group = models.IntegerField(null=True, blank=True)
    expires = models.DateTimeField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "hosts_log"


class HostsToGroupsLog(models.Model):
    id = models.IntegerField()
    mac = models.TextField()  # This field type is a guess.
    gid = models.IntegerField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "hosts_to_groups_log"


class HostsToPoolsLog(models.Model):
    id = models.IntegerField()
    mac = models.TextField()  # This field type is a guess.
    pool_id = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "hosts_to_pools_log"


class InternalAuthLog(models.Model):
    id = models.IntegerField()
    hash = models.CharField(max_length=-1)
    name = models.CharField(max_length=-1, blank=True)
    email = models.CharField(max_length=-1, blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "internal_auth_log"


class KvpLog(models.Model):
    id = models.IntegerField()
    key = models.TextField()
    value = models.TextField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "kvp_log"


class LeasesLog(models.Model):
    address = models.GenericIPAddressField()
    mac = models.TextField(blank=True)  # This field type is a guess.
    abandoned = models.BooleanField()
    server = models.CharField(max_length=-1, blank=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField()
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "leases_log"


class LeasesLog1(models.Model):
    address = models.GenericIPAddressField()
    mac = models.TextField(blank=True)  # This field type is a guess.
    abandoned = models.BooleanField()
    server = models.CharField(max_length=-1, blank=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField()
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "leases_log_1"


class LeasesLog2(models.Model):
    address = models.GenericIPAddressField()
    mac = models.TextField(blank=True)  # This field type is a guess.
    abandoned = models.BooleanField()
    server = models.CharField(max_length=-1, blank=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField()
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "leases_log_2"


class LeasesLogAllV(models.Model):
    address = models.GenericIPAddressField(null=True, blank=True)
    mac = models.TextField(blank=True)  # This field type is a guess.
    abandoned = models.BooleanField(null=True, blank=True)
    server = models.CharField(max_length=-1, blank=True)
    starts = models.DateTimeField(null=True, blank=True)
    ends = models.DateTimeField(null=True, blank=True)
    trigger_mode = models.CharField(max_length=10, blank=True)
    trigger_tuple = models.CharField(max_length=5, blank=True)
    trigger_changed = models.DateTimeField(null=True, blank=True)
    trigger_id = models.BigIntegerField(null=True, blank=True)
    trigger_user = models.CharField(max_length=32, blank=True)

    class Meta:
        managed = False
        db_table = "leases_log_all_v"


class NetworksLog(models.Model):
    network = models.TextField()  # This field type is a guess.
    name = models.CharField(max_length=255, blank=True)
    gateway = models.GenericIPAddressField(null=True, blank=True)
    description = models.TextField(blank=True)
    dhcp_group = models.IntegerField(null=True, blank=True)
    shared_network = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "networks_log"


class NetworksToGroupsLog(models.Model):
    id = models.IntegerField()
    nid = models.TextField()  # This field type is a guess.
    gid = models.IntegerField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "networks_to_groups_log"


class NetworksToVlansLog(models.Model):
    network = models.TextField()  # This field type is a guess.
    vlan = models.SmallIntegerField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "networks_to_vlans_log"


class NotificationsLog(models.Model):
    id = models.IntegerField()
    notification = models.TextField(blank=True)  # This field type is a guess.
    min_permissions = models.TextField()  # This field type is a guess.
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "notifications_log"


class NotificationsToHostsLog(models.Model):
    id = models.IntegerField()
    nid = models.IntegerField()
    mac = models.TextField()  # This field type is a guess.
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "notifications_to_hosts_log"


class PermissionsLog(models.Model):
    id = models.TextField()  # This field type is a guess.
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "permissions_log"


class PoolsLog(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=-1)
    description = models.TextField(blank=True)
    allow_unknown = models.BooleanField()
    lease_time = models.IntegerField()
    dhcp_group = models.IntegerField(null=True, blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "pools_log"


class PoolsToGroupsLog(models.Model):
    id = models.IntegerField()
    pool = models.IntegerField()
    gid = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "pools_to_groups_log"


class SharedNetworksLog(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "shared_networks_log"


class StructuredAttributeValuesLog(models.Model):
    id = models.IntegerField()
    aid = models.IntegerField()
    value = models.TextField()
    is_default = models.BooleanField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "structured_attribute_values_log"


class StructuredAttributesToHostsLog(models.Model):
    id = models.IntegerField()
    mac = models.TextField()  # This field type is a guess.
    avid = models.IntegerField()
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "structured_attributes_to_hosts_log"


class SupermastersLog(models.Model):
    id = models.IntegerField()
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "supermasters_log"


class UsersLog(models.Model):
    id = models.IntegerField()
    username = models.CharField(max_length=50)
    source = models.IntegerField()
    min_permissions = models.TextField()  # This field type is a guess.
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "users_log"


class UsersToGroupsLog(models.Model):
    id = models.IntegerField()
    uid = models.IntegerField()
    gid = models.IntegerField()
    permissions = models.TextField()  # This field type is a guess.
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)
    host_permissions = models.TextField(blank=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "users_to_groups_log"


class VlansLog(models.Model):
    id = models.SmallIntegerField()
    name = models.CharField(max_length=12)
    description = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.IntegerField()
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "vlans_log"
