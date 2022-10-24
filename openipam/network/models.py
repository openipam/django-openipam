from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_save, pre_delete, pre_save
from django.utils import timezone

from djorm_pgfulltext.fields import VectorField
from djorm_pgfulltext.models import SearchManager

from netfields import InetAddressField, CidrAddressField

from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager

from openipam.network.managers import (
    LeaseManager,
    PoolManager,
    DhcpGroupManager,
    DefaultPoolManager,
    AddressTypeManager,
    AddressManager,
    AddressQuerySet,
    NetworkManager,
    NetworkQuerySet,
)
from openipam.network.signals import (
    validate_address_type,
    release_leases,
    set_default_pool,
)
from openipam.user.signals import remove_obj_perms_connected_with_user

import binascii


class Lease(models.Model):
    address = models.OneToOneField(
        "Address",
        primary_key=True,
        db_column="address",
        related_name="leases",
        on_delete=models.CASCADE,
    )
    host = models.ForeignKey(
        "hosts.Host",
        db_column="mac",
        db_constraint=False,
        related_name="leases",
        null=True,
        on_delete=models.DO_NOTHING,
    )
    abandoned = models.BooleanField(default=False)
    server = models.CharField(max_length=255, blank=True, null=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()

    objects = LeaseManager()

    def __str__(self):
        return "%s" % self.pk

    @property
    def is_expired(self):
        return True if self.ends <= timezone.now() else False

    @property
    def gul_last_seen(self):
        from openipam.hosts.models import GulRecentArpByaddress

        ls = (
            GulRecentArpByaddress.objects.filter(address=self.address.address)
            .order_by("-stopstamp")
            .first()
        )
        return ls.stopstamp if ls else None

    @property
    def gul_last_seen_mac(self):
        from openipam.hosts.models import GulRecentArpByaddress

        if self.host:
            try:
                return GulRecentArpByaddress.objects.get(
                    address=self.address.address
                ).host
            except GulRecentArpByaddress.DoesNotExist:
                return None
        else:
            return None

    class Meta:
        db_table = "leases"


class Pool(models.Model):
    name = models.SlugField()
    description = models.TextField(blank=True)
    allow_unknown = models.BooleanField(default=False)
    lease_time = models.IntegerField()
    assignable = models.BooleanField(default=False)
    dhcp_group = models.ForeignKey(
        "DhcpGroup",
        null=True,
        db_column="dhcp_group",
        blank=True,
        on_delete=models.PROTECT,
    )

    objects = PoolManager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pools"
        permissions = (("add_records_to_pool", "Can add records to"),)


class DefaultPool(models.Model):
    pool = models.ForeignKey(
        "Pool",
        related_name="pool_defaults",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    cidr = CidrAddressField(unique=True)

    objects = DefaultPoolManager()

    def __str__(self):
        return "%s - %s" % (self.pool, self.cidr)

    class Meta:
        db_table = "default_pools"


class DhcpGroup(models.Model):
    name = models.SlugField()
    description = models.TextField(blank=True, null=True)
    dhcp_options = models.ManyToManyField("DhcpOption", through="DhcpOptionToDhcpGroup")
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    objects = DhcpGroupManager()

    def __str__(self):
        return "%s" % self.name

    class Meta:
        db_table = "dhcp_groups"
        verbose_name = "DHCP group"


class DhcpOption(models.Model):
    size = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    option = models.CharField(max_length=255, unique=True, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        db_table = "dhcp_options"
        verbose_name = "DHCP option"


class DhcpOptionToDhcpGroup(models.Model):
    group = models.ForeignKey(
        "DhcpGroup",
        null=True,
        db_column="gid",
        blank=True,
        related_name="option_values",
        on_delete=models.CASCADE,
    )
    option = models.ForeignKey(
        "DhcpOption",
        null=True,
        db_column="oid",
        blank=True,
        related_name="group_values",
        on_delete=models.PROTECT,
    )
    value = models.BinaryField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    @staticmethod
    def is_displayable_byte(byte):
        # include normal printables, exclude DEL
        if byte >= 32 and byte < 127:
            return True
        return False

    @classmethod
    def is_displayable(self, value):
        return all(self.is_displayable_byte(b) for b in value) if value else None

    def displayable_value(self, repr_ascii=False):
        value = self.value
        if not value:
            return None
        if hasattr(value, "tobytes"):
            value = value.tobytes()
        elif isinstance(value, str):
            value = value.encode()

        use_ascii = self.is_displayable(value)

        if use_ascii:
            displayable = value.decode(encoding="ascii")
            if repr_ascii:
                return repr(displayable)
            return displayable
        return "0x" + value.hex()

    @property
    def value_fordisplay(self):
        return self.displayable_value(repr_ascii=True)

    @property
    def value_foredit(self):
        return self.displayable_value(repr_ascii=False)

    def __str__(self):
        return "%s:%s=%s" % (self.group.name, self.option.name, self.value_fordisplay)

    def get_readable_value(self):
        if self.value:
            return binascii.hexlify(self.value)
        return None

    class Meta:
        db_table = "dhcp_options_to_dhcp_groups"


class HostToPool(models.Model):
    host = models.ForeignKey(
        "hosts.Host",
        db_column="mac",
        db_index=True,
        related_name="host_pools",
        on_delete=models.CASCADE,
    )
    pool = models.ForeignKey(
        "Pool", db_index=True, related_name="host_pools", on_delete=models.CASCADE
    )
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return "%s %s" % (self.host.hostname, self.pool.name)

    class Meta:
        db_table = "hosts_to_pools"


class SharedNetwork(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "shared_networks"


class TaggedNetworks(TaggedItemBase):
    content_object = models.ForeignKey("Network", on_delete=models.CASCADE)


class Network(models.Model):
    network = CidrAddressField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    gateway = InetAddressField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    vlans = models.ManyToManyField(
        "Vlan", through="NetworkToVlan", related_name="vlan_networks"
    )
    dhcp_group = models.ForeignKey(
        "DhcpGroup",
        db_column="dhcp_group",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    shared_network = models.ForeignKey(
        "SharedNetwork",
        db_column="shared_network",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    search_index = VectorField()

    # objects = NetworkQuerySet.as_manager()
    objects = NetworkManager.from_queryset(NetworkQuerySet)()

    searcher = SearchManager(
        fields=("name", "description"),
        config="pg_catalog.english",  # this is default
        search_field="search_index",  # this is default
        auto_update_search_field=True,
    )

    tags = TaggableManager(through=TaggedNetworks, blank=True)

    # Forcing pk as string
    @property
    def pk(self):
        return str(self.network)

    def __str__(self):
        return "%s" % self.network

    class Meta:
        db_table = "networks"
        permissions = (
            ("is_owner_network", "Is owner"),
            ("add_records_to_network", "Can add records to"),
        )
        default_permissions = ("add", "change", "delete", "view")
        ordering = ("network",)


class NetworkRange(models.Model):
    range = CidrAddressField(unique=True)

    def __str__(self):
        return "%s" % self.range

    class Meta:
        db_table = "network_ranges"


class Vlan(models.Model):
    vlan_id = models.SmallIntegerField()
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    buildings = models.ManyToManyField(
        "Building", through="BuildingToVlan", related_name="building_vlans"
    )
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return "%s %s" % (self.vlan_id, self.name)

    class Meta:
        db_table = "vlans"


class NetworkToVlan(models.Model):
    network = models.OneToOneField(
        "Network", primary_key=True, db_column="network", on_delete=models.CASCADE
    )
    vlan = models.ForeignKey("Vlan", db_column="vlan", on_delete=models.CASCADE)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return "%s %s" % (self.network, self.vlan)

    class Meta:
        db_table = "networks_to_vlans"


class Building(models.Model):
    name = models.CharField(max_length=255, blank=True)
    number = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return "%s - %s" % (self.number, self.name)

    class Meta:
        db_table = "buildings"


class BuildingToVlan(models.Model):
    building = models.ForeignKey(
        "Building", db_column="building", on_delete=models.CASCADE
    )
    vlan = models.ForeignKey("Vlan", db_column="vlan", on_delete=models.CASCADE)
    tagged = models.BooleanField(default=False)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    class Meta:
        db_table = "buildings_to_vlans"
        unique_together = ["building", "vlan"]


class Address(models.Model):
    address = InetAddressField(primary_key=True, store_prefix_length=False)
    # Force manual removal of addresses so they are unassigned and properly re-classified
    host = models.ForeignKey(
        "hosts.Host",
        db_column="mac",
        blank=True,
        null=True,
        related_name="addresses",
        on_delete=models.SET_NULL,
    )
    pool = models.ForeignKey(
        "Pool", db_column="pool", blank=True, null=True, on_delete=models.SET_NULL
    )
    reserved = models.BooleanField(default=False)
    # Do we want to allow deletion of a network with addresses referencing it?
    network = models.ForeignKey(
        "Network",
        db_column="network",
        related_name="net_addresses",
        on_delete=models.CASCADE,
    )
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    # objects = AddressQuerySet.as_manager()
    objects = AddressManager.from_queryset(AddressQuerySet)()

    def __str__(self):
        return str(self.address)

    @property
    def last_mac_seen(self):
        from openipam.hosts.models import GulRecentArpBymac

        gul_mac = (
            GulRecentArpBymac.objects.filter(mac=self.mac)
            .order_by("-stopstamp")
            .first()
        )
        return gul_mac[0].mac if gul_mac else None

    @property
    def last_seen(self):
        from openipam.hosts.models import GulRecentArpByaddress

        gul_ip = (
            GulRecentArpByaddress.objects.filter(address=self.address)
            .order_by("-stopstamp")
            .first()
        )
        return gul_ip.stopstamp if gul_ip else None

    def clean(self):
        if self.host and self.pool:
            raise ValidationError(
                "Host and Pool cannot both be defined.  Choose one or the other."
            )
        elif (self.host or self.pool) and self.reserved:
            raise ValidationError(
                "If a Host or Pool are defined, reserved must be false."
            )
        elif self.address not in self.network.network:
            raise ValidationError(
                "Address entered must be a part of the network selected."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Address, self).save(*args, **kwargs)

    class Meta:
        db_table = "addresses"
        verbose_name_plural = "addresses"


class AddressType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ranges = models.ManyToManyField(
        "NetworkRange", related_name="address_ranges", blank=True
    )
    pool = models.ForeignKey("Pool", blank=True, null=True, on_delete=models.SET_NULL)
    is_default = models.BooleanField(default=False)

    objects = AddressTypeManager()

    def __str__(self):
        return self.description

    def clean(self):
        if self.is_default:
            default_exists = (
                AddressType.objects.filter(is_default=True).exclude(pk=self.pk).first()
            )
            if default_exists:
                raise ValidationError(
                    "Default already assined to '%s'. There can only be one default Address Type"
                    % default_exists.name
                )

    class Meta:
        db_table = "addresstypes"
        ordering = ("name",)


# Network Signals
pre_save.connect(set_default_pool, sender=Address)
m2m_changed.connect(validate_address_type, sender=AddressType.ranges.through)
post_save.connect(release_leases, sender=Address)
pre_delete.connect(remove_obj_perms_connected_with_user, sender=Network)
pre_delete.connect(remove_obj_perms_connected_with_user, sender=DhcpOption)
