from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import utc
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete
from django.db import connection
from django.core.validators import validate_ipv46_address
from django.utils.functional import cached_property
from django.contrib.contenttypes.models import ContentType
from django.db.utils import DatabaseError
from django.db import transaction

from netfields import MACAddressField, NetManager

from djorm_pgfulltext.fields import VectorField
from djorm_pgfulltext.models import SearchManager

from guardian.shortcuts import get_objects_for_user, remove_perm, assign_perm
from guardian.models import UserObjectPermission, GroupObjectPermission

from openipam.core.mixins import DirtyFieldsMixin
from openipam.hosts.validators import validate_hostname
from openipam.hosts.managers import HostManager, HostQuerySet
from openipam.user.signals import remove_obj_perms_connected_with_user
from openipam.dns.models import DhcpDnsRecord

from datetime import datetime, timedelta

import string
import random

from six import string_types

User = get_user_model()


class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    structured = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    validation = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "attributes"


class AttributeToHost(models.Model):
    attribute = models.IntegerField(null=True, blank=True, db_column="aid")
    name = models.CharField(max_length=255, blank=True, null=True)
    structured = models.BooleanField(default=None)
    required = models.BooleanField(default=False)
    mac = MACAddressField(blank=True, null=True)
    avid = models.IntegerField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    objects = NetManager()

    def __str__(self):
        return "%s %s" % (self.attribute.name, self.name)

    class Meta:
        managed = False
        db_table = "attributes_to_hosts"


class Disabled(models.Model):
    mac = MACAddressField(primary_key=True)
    reason = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True, db_column="disabled")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="disabled_by", on_delete=models.PROTECT
    )

    def __init__(self, *args, **kwargs):
        # Initialize setters
        self._host = None

        super(Disabled, self).__init__(*args, **kwargs)

    def __str__(self):
        return "%s" % self.pk

    @property
    def host(self):
        if self._host:
            return self._host
        else:
            host_obj = Host.objects.filter(mac=self.mac).first()
            return host_obj.hostname if host_obj else None

    @host.setter
    def host(self, host):
        self._host = host

    class Meta:
        db_table = "disabled"
        verbose_name = "Disabled Host"
        ordering = ("-changed",)


class ExpirationType(models.Model):
    expiration = models.DateTimeField()
    min_permissions = models.CharField(max_length=8)  # FIXME

    def __str__(self):
        return "%s days" % self.expiration.days

    class Meta:
        db_table = "expiration_types"
        ordering = ("expiration",)
        permissions = (("is_owner_expiration_type", "Is owner"),)


class FreeformAttributeToHost(models.Model):
    host = models.ForeignKey(
        "Host",
        db_column="mac",
        related_name="freeform_attributes",
        on_delete=models.CASCADE,
    )
    attribute = models.ForeignKey(
        "Attribute", db_column="aid", on_delete=models.PROTECT
    )
    value = models.TextField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return "%s %s %s" % (self.pk, self.attribute.name, self.value)

    class Meta:
        db_table = "freeform_attributes_to_hosts"


class GuestTicket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="uid", on_delete=models.CASCADE
    )
    ticket = models.CharField(max_length=255, unique=True)
    starts = models.DateTimeField()
    ends = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.ticket

    def set_ticket(self):
        """Generates a human-readable string for a ticket."""

        def generate_random_ticket():
            vowels = ("a", "e", "i", "o", "u")
            consonants = [a for a in string.ascii_lowercase if a not in vowels]
            groups = ("th", "ch", "sh", "kl", "gr", "br")

            num_vowels = len(vowels) - 1
            num_consonants = len(consonants) - 1
            num_groups = len(groups) - 1

            vowel = []
            cons = []
            group = []

            for i in range(4):
                vowel.append(vowels[random.randint(0, num_vowels)])
                cons.append(consonants[random.randint(0, num_consonants)])
                group.append(groups[random.randint(0, num_groups)])

            structure = []
            structure.append(
                "%s%s%s%s%s%s%s%s"
                % (
                    cons[0],
                    vowel[0],
                    cons[1],
                    cons[2],
                    vowel[1],
                    cons[3],
                    vowel[2],
                    group[0],
                )
            )
            structure.append(
                "%s%s%s%s%s%s"
                % (group[0], vowel[0], cons[0], cons[1], vowel[1], group[1])
            )
            structure.append(
                "%s%s%s%s%s" % (group[0], vowel[0], cons[0], vowel[1], "s")
            )
            structure.append(
                "%s%s%s%s%s" % (vowel[0], group[0], vowel[1], cons[0], vowel[2])
            )
            structure.append(
                "%s%s%s%s%s" % (group[0], vowel[0], cons[0], vowel[1], group[1])
            )
            structure.append("%s%s%s%s" % (vowel[0], group[0], vowel[1], group[1]))
            structure.append(
                "%s%s%s%s%s%s%s%s"
                % (
                    cons[0],
                    vowel[0],
                    cons[1],
                    vowel[1],
                    cons[2],
                    vowel[2],
                    cons[3],
                    vowel[2],
                )
            )
            structure.append(
                "%s%s%s%s%s" % (group[0], vowel[1], group[1], vowel[1], cons[0])
            )

            return structure[random.randint(0, len(structure) - 1)]

        ticket = generate_random_ticket()
        while GuestTicket.objects.filter(ticket=ticket):
            ticket = generate_random_ticket()

        self.ticket = ticket

    class Meta:
        db_table = "guest_tickets"


class GulRecentArpByaddress(models.Model):
    host = models.OneToOneField(
        "Host",
        on_delete=models.DO_NOTHING,
        db_column="mac",
        db_constraint=False,
        related_name="ip_history",
        primary_key=True,
    )
    address = models.ForeignKey(
        "network.Address",
        on_delete=models.DO_NOTHING,
        db_column="address",
        db_constraint=False,
        related_name="ip_history",
    )
    stopstamp = models.DateTimeField()

    objects = NetManager()

    def __str__(self):
        return "%s - %s" % (self.pk, self.address_id)

    class Meta:
        db_table = "gul_recent_arp_byaddress"
        managed = False


class GulRecentArpBymac(models.Model):
    host = models.OneToOneField(
        "Host",
        on_delete=models.DO_NOTHING,
        db_column="mac",
        db_constraint=False,
        related_name="mac_history",
        primary_key=True,
    )
    address = models.ForeignKey(
        "network.Address",
        on_delete=models.DO_NOTHING,
        db_column="address",
        db_constraint=False,
        related_name="mac_history",
    )
    stopstamp = models.DateTimeField()

    objects = NetManager()

    def __str__(self):
        return "%s - %s" % (self.pk, self.address)

    class Meta:
        db_table = "gul_recent_arp_bymac"
        managed = False


class HostUserView(models.Model):
    user = models.ForeignKey(
        User, primary_key=True, db_column="user", on_delete=models.DO_NOTHING
    )
    host = models.ForeignKey(
        "Host",
        db_column="mac",
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        unique_together = (("user", "host"),)
        managed = False
        db_table = "hosts_to_auth_users_v"


class HostGroupView(models.Model):
    group_id = models.ForeignKey(
        "auth.Group",
        primary_key=True,
        db_column="auth_group",
        on_delete=models.DO_NOTHING,
    )
    group_name = models.CharField(max_length=80, db_column="auth_group_name")
    host = models.ForeignKey(
        "Host",
        db_column="mac",
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        unique_together = (("group_id", "group_name", "host"),)
        managed = False
        db_table = "hosts_to_auth_groups_v"


class Host(DirtyFieldsMixin, models.Model):
    mac = MACAddressField("Mac Address", primary_key=True)
    hostname = models.CharField(
        max_length=255, unique=True, validators=[validate_hostname], db_index=True
    )
    description = models.TextField(blank=True, null=True)
    address_type_id = models.ForeignKey(
        "network.AddressType",
        blank=True,
        null=True,
        db_column="address_type_id",
        on_delete=models.SET_NULL,
    )
    pools = models.ManyToManyField(
        "network.Pool", through="network.HostToPool", related_name="pool_hosts"
    )
    dhcp_group = models.ForeignKey(
        "network.DhcpGroup",
        db_column="dhcp_group",
        verbose_name="DHCP Group",
        blank=True,
        null=True,
        on_delete=models.PROTECT,  # This was SET_NULL before, wrong?
    )
    expires = models.DateTimeField()
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )
    last_notified = models.DateTimeField(blank=True, null=True)

    objects = HostManager.from_queryset(HostQuerySet)()

    search_index = VectorField()
    searcher = SearchManager(
        fields=("hostname", "description"),
        config="pg_catalog.english",  # this is default
        search_field="search_index",  # this is default
        auto_update_search_field=True,
    )

    def __init__(self, *args, **kwargs):

        # Initialize setters
        self._expire_days = None
        self._user_owners = None
        self._group_owners = None
        self._user = None
        self._master_dns_deleted = False

        self.ip_address = None
        self.pool = None
        self.network = None

        super(Host, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.hostname

    # Overload getattr for get original values
    def __getattr__(self, name):
        if name.startswith("original_") and name.split("_", 1)[1] in list(
            self._original_state.keys()
        ):

            def _original(fieldname):
                fieldvalue = self._original_state.get(fieldname, None)
                if fieldvalue is not None:
                    return fieldvalue

            return _original(name.split("_", 1)[1])
        else:
            return self.__getattribute__(name)

    def reset_state(self):
        self._expire_days = None
        self._user_owners = None
        self._group_owners = None
        self._user = None
        self._master_dns_deleted = False

        self.ip_address = None
        self.pool = None
        self.network = None

        try:
            del self.ip_addresses
            del self.master_ip_address
            del self.owners
            del self._pools_cache
            del self._addresses_cache
        except AttributeError:
            pass

    @cached_property
    def _addresses_cache(self):
        return list(self.addresses.all())

    @cached_property
    def _pools_cache(self):
        return list(self.pools.all())

    @property
    def expire_days(self):
        if self._expire_days:
            return self._expire_days
        else:
            return self.get_expire_days()

    @expire_days.setter
    def expire_days(self, days):
        self._expire_days = days

    @cached_property
    def owners(self):
        return self.get_owners()

    def get_owners(
        self,
        ids_only=False,
        name_only=False,
        owner_detail=False,
        users_only=False,
        user_perms_prefetch=None,
        group_perms_prefetch=None,
    ):
        # users_dict = get_users_with_perms(self, attach_perms=True, with_group_users=False)
        # groups_dict = get_groups_with_perms(self, attach_perms=True)
        content_type = ContentType.objects.get_for_model(self)

        users = []
        if user_perms_prefetch:
            user_perms = list(
                filter(
                    lambda x: x.object_pk == str(self.mac)
                    and x.permission.codename == "is_owner_host",
                    user_perms_prefetch,
                )
            )
        else:
            user_perms = UserObjectPermission.objects.filter(
                content_type=content_type,
                object_pk=str(self.mac),
                permission__codename="is_owner_host",
            )
        for perm in user_perms:
            users.append(perm.user)

        groups = []
        if group_perms_prefetch:
            group_perms = list(
                filter(
                    lambda x: x.object_pk == str(self.mac)
                    and x.permission.codename == "is_owner_host",
                    group_perms_prefetch,
                )
            )
        else:
            group_perms = GroupObjectPermission.objects.filter(
                content_type=content_type,
                object_pk=str(self.mac),
                permission__codename="is_owner_host",
            )
        for perm in group_perms:
            groups.append(perm.group)

        # for user, permissions in users_dict.iteritems():
        #    if 'is_owner_host' in permissions:
        #        users.append(user)

        # groups = []
        # for group, permissions in groups_dict.iteritems():
        #    if 'is_owner_host' in permissions:
        #        groups.append(group)

        if users_only:
            users_from_groups = [
                user for user in User.objects.filter(groups__in=groups)
            ]
            users = list(set(users + users_from_groups))
            return users

        if owner_detail:
            users = [
                (user.pk, user.username, user.get_full_name(), user.email)
                for user in users
            ]
            groups = [(group.pk, group.name) for group in groups]

        elif ids_only:
            users = [user.pk for user in users]
            groups = [group.pk for group in groups]

        elif name_only:
            users = [user.username for user in users]
            groups = [group.name for group in groups]

        return users, groups

    @property
    def user_owners(self):
        if self._user_owners:
            return self._user_owners
        else:
            return [owner.username for owner in self.owners[0]]

    @user_owners.setter
    def user_owners(self, owners):
        self._user_owners = owners

    @property
    def user(self):
        if self._user:
            return self._user
        else:
            return self.changed_by

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def master_dns_deleted(self):
        return self._master_dns_deleted

    @master_dns_deleted.setter
    def master_dns_deleted(self, value):
        self._master_dns_deleted = value

    @property
    def group_owners(self):
        if self._group_owners:
            return self._group_owners
        else:
            return [owner.name for owner in self.owners[1]]

    @group_owners.setter
    def group_owners(self, owners):
        self._group_owners = owners

    @property
    def is_dynamic(self):
        if self.is_dirty() is False:
            return True if self._pools_cache else False
        else:
            return True if self.pools.all() else False

    @property
    def is_static(self):
        return True if self.is_dynamic is False else False

    # This is set on the queryset manager now.
    # @property
    # def is_disabled(self):
    #     try:
    #         return True if self.disabled_host else False
    #     except ObjectDoesNotExist:
    #         return False

    @property
    def disabled_host(self):
        if self.is_disabled:
            return Disabled.objects.filter(pk=self.mac).first()
        else:
            return None

    @property
    def is_expired(self):
        return True if self.expires < timezone.now() else False

    @property
    def address_type(self):
        # TODO: Address type is old and eventually will be deprecated.
        # Try to set address type if doesn't exist if host already exists in DB.
        if self.pk and not self.address_type_id:
            from openipam.network.models import AddressType, NetworkRange

            addresses = self._addresses_cache
            pools = self._pools_cache

            try:
                # if (len(addresses) + len(pools)) > 1:
                #     self.address_type = None
                # elif addresses:
                if addresses:
                    try:
                        ranges = NetworkRange.objects.filter(
                            range__net_contains_or_equals=addresses[0].address
                        )
                        if ranges:
                            self.address_type_id = AddressType.objects.get(
                                ranges__in=ranges
                            )
                        else:
                            raise AddressType.DoesNotExist
                    except AddressType.DoesNotExist:
                        self.address_type_id = AddressType.objects.get(is_default=True)
                elif pools:
                    self.address_type_id = AddressType.objects.get(pool=pools[0])
            except AddressType.DoesNotExist:
                self.address_type_id = None

        return self.address_type_id

    @address_type.setter
    def address_type(self, value):
        self.address_type_id = value

    @property
    def mac_stripped(self):
        mac = str(self.mac)
        mac = [c for c in mac if c.isdigit() or c.isalpha()]
        return "".join(mac)

    @property
    def mac_last_seen(self):
        gul_mac = GulRecentArpBymac.objects.filter(pk=self.mac).order_by("-stopstamp")

        if gul_mac:
            return gul_mac[0].stopstamp
        else:
            return None

    @property
    def mac_last_seen_by_host(self):
        gul_mac = GulRecentArpBymac.objects.filter(host=self).order_by("-stopstamp")

        print(gul_mac)
        return gul_mac[0].stopstamp if gul_mac else None

    @property
    def oui(self):
        return OUI.objects.extra(
            where=["'%s' >= ouis.start and '%s' <= ouis.stop" % (self.mac, self.mac)]
        ).first()

    @cached_property
    def master_ip_address(self):
        if self.is_static:
            if not self.ip_addresses:
                return None
            elif len(self.ip_addresses) == 1:
                return self.ip_addresses[0]
            else:
                address = self.addresses.filter(arecords__name=self.hostname).first()
                return str(address) if address else self.ip_addresses[0]
        return None

    @cached_property
    def ip_addresses(self):
        return [str(address) for address in self.addresses.all()]

    def delete_ip_address(self, user, address):

        if isinstance(address, string_types):
            address = self.addresses.filter(address=address)

        # Delete DNS PTR and A Records
        self.delete_dns_records(user=user, addresses=address)

        # Release address
        address.release(user=user)

    def add_ip_address(self, user=None, ip_address=None, network=None, hostname=None):
        from openipam.network.models import Network, Address
        from openipam.dns.models import DnsRecord, DnsType

        user = user or self._user
        if not user:
            raise Exception("A User must be given to add ip addresses.")

        if not hostname:
            raise ValidationError("A hostname is required.")

        address = None

        # Check to see if hostname already taken for any
        # hosts other then the current one if being updated.
        used_hostname = (
            DnsRecord.objects.filter(
                dns_type__in=[DnsType.objects.A, DnsType.objects.AAAA], name=hostname
            )
            .exclude(ip_content__address=self.master_ip_address)
            .first()
        )
        if used_hostname:
            raise ValidationError(
                "Hostname %s is already assigned to DNS A Record: %s."
                % (hostname, used_hostname.ip_content)
            )

        user_pools = get_objects_for_user(
            user, ["network.add_records_to_pool", "network.change_pool"], any_perm=True
        )

        user_nets = get_objects_for_user(
            user,
            [
                "network.add_records_to_network",
                "network.is_owner_network",
                "network.change_network",
            ],
            any_perm=True,
        )

        if network:
            if isinstance(network, string_types):
                network = Network.objects.get(network=network)

            if not user_nets.filter(network=network.network):
                raise ValidationError(
                    "You do not have access to assign host '%s' to the "
                    "network specified: %s." % (hostname, network)
                )

            try:
                network_address = (
                    Address.objects.filter(
                        Q(pool__in=user_pools) | Q(pool__isnull=True),
                        Q(leases__isnull=True)
                        | Q(leases__abandoned=True)
                        | Q(leases__ends__lte=timezone.now())
                        | Q(leases__host=self),
                        network=network,
                        host__isnull=True,
                        reserved=False,
                    )
                    .order_by("address")
                    .first()
                )

                if not network_address:
                    raise Address.DoesNotExist
                else:
                    address = network_address

            except ValidationError:
                raise ValidationError("The network '%s' is invalid." % network)
            except Address.DoesNotExist:
                raise ValidationError(
                    "There are no avaiable addresses for the network entered: %s"
                    % network
                )

        elif ip_address:
            # Validate IP Address
            try:
                validate_ipv46_address(ip_address)
            except ValidationError:
                raise ValidationError(
                    "IP Address %s is invalid.  Enter a valid IPv4 or IPv6 address."
                    % ip_address
                )

            if ip_address in self.ip_addresses:
                raise ValidationError(
                    "IP address %s is already assigned to this host." % ip_address
                )

            try:
                address = Address.objects.get(
                    Q(pool__in=user_pools)
                    | Q(pool__isnull=True)
                    | Q(network__in=user_nets),
                    Q(leases__isnull=True)
                    | Q(leases__abandoned=True)
                    | Q(leases__ends__lte=timezone.now())
                    | Q(leases__host=self),
                    Q(host__isnull=True) | Q(host=self),
                    address=ip_address,
                    reserved=False,
                )
            except ValidationError:
                raise ValidationError(
                    "There IP Address %s is not available." % ip_address
                )
            except Address.DoesNotExist:
                raise ValidationError(
                    "There are no avaiable addresses for the IP entered: %s"
                    % ip_address
                )
        else:
            raise ValidationError(
                "A Network or IP Address must be given to assign this host an address."
            )

        # Make sure pool is clear on addresses we are assigning.
        address.pool_id = None
        address.host = self
        address.changed_by = user
        address.save()

        # Update A and PTR dns records
        self.add_dns_records(user=user, hostname=hostname, address=address)

        return address

    def delete_dns_records(
        self, user=None, delete_only_master_dns=False, delete_dchpdns=True, addresses=[]
    ):
        from openipam.dns.models import DnsType

        user = user or self._user
        if not user:
            raise Exception("A User must be given to delete dns records for host.")

        if self.master_dns_deleted is False:

            # If addresses list is empty, we use the master address
            # So By default we are deleting DNS for just the primary address
            if not addresses:
                addresses = self.addresses.filter(address=self.master_ip_address)

            if delete_only_master_dns:
                # Here we only delete the master DNS (A and PTR) record
                # If modifying a host, this will get recreated later in the call.
                self.dns_records.filter(
                    Q(name=self.original_hostname)
                    | Q(text_content=self.original_hostname),
                    dns_type__in=[
                        DnsType.objects.PTR,
                        DnsType.objects.A,
                        DnsType.objects.AAAA,
                    ],
                ).update(changed=timezone.now(), changed_by=user)
                # Delete Assocatiated PTR and A or AAAA records.
                self.dns_records.filter(
                    Q(name=self.original_hostname)
                    | Q(text_content=self.original_hostname),
                    dns_type__in=[
                        DnsType.objects.PTR,
                        DnsType.objects.A,
                        DnsType.objects.AAAA,
                    ],
                ).delete()
            else:
                # TODO: There is a foreign key for host on this table but we cant use it
                # cause are aren't sure this will get everything due to not all records
                # using the FK.
                # Update Changed by Assocatiated PTR and A or AAAA records.
                self.dns_records.filter(
                    Q(
                        name__in=[
                            address.address.reverse_pointer for address in addresses
                        ]
                    )
                    | Q(ip_content__in=[address for address in addresses]),
                    dns_type__in=[
                        DnsType.objects.PTR,
                        DnsType.objects.A,
                        DnsType.objects.AAAA,
                    ],
                ).update(changed=timezone.now(), changed_by=user)
                # Delete Assocatiated PTR and A or AAAA records.
                self.dns_records.filter(
                    Q(
                        name__in=[
                            address.address.reverse_pointer for address in addresses
                        ]
                    )
                    | Q(ip_content__in=[address for address in addresses]),
                    dns_type__in=[
                        DnsType.objects.PTR,
                        DnsType.objects.A,
                        DnsType.objects.AAAA,
                    ],
                ).delete()

            if delete_dchpdns:
                # Delete DHCP DNS records for dynamics if they exist.
                DhcpDnsRecord.objects.filter(
                    host__hostname=self.original_hostname
                ).delete()

            if not addresses or self.master_ip_address in [
                str(address.address) for address in addresses
            ]:
                self.master_dns_deleted = True

    def add_dns_records(self, user=None, hostname=None, address=None):
        from openipam.dns.models import DnsRecord, DnsType
        from openipam.network.models import Address

        user = user or self._user
        if not user:
            raise Exception("A User must be given to add dns records for host.")

        # Only do this on static hosts.
        if self.is_static:

            if not hostname:
                hostname = self.hostname

            if isinstance(address, string_types):
                address = Address.objects.filter(address=address).first()
            elif not address:
                address = Address.objects.filter(address=self.master_ip_address).first()

            # Add Associated PTR
            DnsRecord.objects.add_or_update_record(
                user=user,
                name=address.address.reverse_pointer,
                content=hostname,
                dns_type=DnsType.objects.PTR,
                host=self,
            )

            # Add Associated A or AAAA record
            arecord = DnsRecord.objects.filter(
                dns_type__in=[DnsType.objects.A, DnsType.objects.AAAA],
                host=self,
                name=hostname,
            ).first()
            DnsRecord.objects.add_or_update_record(
                user=user,
                name=hostname,
                content=address.address,
                dns_type=DnsType.objects.A
                if address.address.version == 4
                else DnsType.objects.AAAA,
                host=self,
                record=arecord if arecord else None,
            )

        # Reset dns deleted flag if this is the master hostname
        if hostname == self.hostname:
            self.master_dns_deleted = False

    def get_dns_records(self):
        from openipam.dns.models import DnsRecord

        addresses = self.addresses.all()
        a_record_names = (
            DnsRecord.objects.select_related("ip_content", "host", "dns_type")
            .filter(ip_content__in=addresses)
            .values_list("name")
        )
        dns_records = (
            DnsRecord.objects.select_related("ip_content", "host", "dns_type")
            .filter(
                Q(text_content__in=a_record_names)
                | Q(name__in=a_record_names)
                | Q(ip_content__in=addresses)
                | Q(host=self)
                | Q(text_content=self.hostname)  # For dynamic hosts
            )
            .order_by("dns_type__name")
        )

        return dns_records

    def get_expire_days(self):
        if self.expires:
            delta = self.expires - timezone.now()
            return delta.days if delta.days > 0 else None
        else:
            return None

    def set_expiration(self, expire_days):
        if isinstance(expire_days, int) or isinstance(expire_days, string_types):
            expire_days = timedelta(int(expire_days))
        now = timezone.now()
        self.expires = (
            datetime(now.year, now.month, now.day) + timedelta(1) + expire_days
        )
        self.expires = self.expires.replace(tzinfo=utc)

    def set_mac_address(self, new_mac_address):
        if self.mac and str(self.mac).lower() != str(new_mac_address).lower():
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE hosts SET mac = %s WHERE mac = %s
            """,
                [str(new_mac_address), str(self.mac)],
            )
            self.mac = str(new_mac_address).lower()
        elif not self.pk:
            self.mac = str(new_mac_address).lower()

    def set_hostname(self, hostname, user=None):
        user = user or self._user
        if not user:
            raise Exception("A User must be given to save hosts.")

        self.hostname = hostname
        if (
            self.original_hostname
            and self.hostname
            and self.hostname != self.original_hostname
        ):
            self.delete_dns_records(user=user, delete_only_master_dns=True)

    # TODO: Clean this up, I dont like where this is at.
    def set_network_ip_or_pool(self, user=None, delete=False):
        user = user or self._user
        if not user:
            raise Exception("A User must be given to save hosts.")

        # Set the pool if attached to model otherwise find it by address type
        pool = self.pool
        current_pool = self._pools_cache[0] if self._pools_cache else None

        # TODO: Currently un-used function
        if delete:
            # Remove all pools
            self.pools.clear()
            # Delete DNS
            self.delete_dns_records(user=user, addresses=self.addresses.all())
            # Remove all addresses
            self.addresses.release(user=user)

        # If we have a pool, this dynamic and we assign
        if pool and pool != current_pool:
            from openipam.network.models import Pool

            # Delete DNS
            self.delete_dns_records(user=user, addresses=self.addresses.all())
            # Remove all addresses
            self.addresses.release(user=user)

            # TODO: Kill this later.
            host_pool_check = self.host_pools.all()
            if len(host_pool_check) > 1:
                self.pools.clear()

            host_pool = self.host_pools.filter(pool__name=pool).first()
            if host_pool:
                host_pool.changed_by = user
                host_pool.save()
            else:
                # Delete what is there and create a new one.
                self.pools.clear()
                # Assign new pool if it doesn't already exist
                self.host_pools.create(
                    host=self, pool=Pool.objects.get(name=pool), changed_by=user
                )

        # If we have a Network or IP address, then assign that address to host
        elif self.network or (
            self.ip_address and self.ip_address not in self.ip_addresses
        ):

            # Remove all pools
            self.pools.clear()
            # TODO: Look at delete_dns for a way to only delete dhcp dns records.
            try:
                self.dhcpdnsrecord.delete()
            except ObjectDoesNotExist:
                pass

            # Current IP
            current_ip_address = self.master_ip_address

            if current_ip_address:
                # Delete DNS
                self.delete_dns_records(user=user)
                # Release the current IP to add another
                self.addresses.filter(address=current_ip_address).release(user=user)

            # Add new IP
            self.add_ip_address(
                user=user,
                ip_address=self.ip_address,
                network=self.network,
                hostname=self.hostname,
            )

    def remove_owners(self):
        users, groups = self.get_owners()
        self.remove_user_owners(users)
        self.remove_group_owners(groups)

    def remove_user_owners(self, users=None):
        if not users:
            users = self.get_owners(users_only=True)
        for user in users:
            remove_perm("is_owner_host", user, self)

    def remove_group_owners(self, groups=None):
        if not groups:
            users, groups = self.get_owners()
        for group in groups:
            remove_perm("is_owner_host", group, self)

    def remove_owner(self, user_or_group):
        return remove_perm("is_owner_host", user_or_group, self)

    def assign_owner(self, user_or_group):
        return assign_perm("is_owner_host", user_or_group, self)

    def save(self, user=None, add_dns=True, *args, **kwargs):
        user = user or self._user
        if not user:
            raise Exception("A User must be given to save hosts.")

        # Make sure hostname is lowercase
        self.hostname = self.hostname.lower()
        # Make sure mac is lowercase
        self.mac = str(self.mac).lower()

        # Updating changed and changed_by
        self.changed_by = user
        self.changed = timezone.now()

        # If master DNS delete, re-create it
        if add_dns and self.master_dns_deleted is True:
            self.add_dns_records(user=user)

        super(Host, self).save(*args, **kwargs)

    def delete(self, user=None, *args, **kwargs):
        user = user or self._user
        if not user:
            raise Exception("A User must be given to save hosts.")

        # Delete primary DNS (PTR, A, and AAAA, updating changed and changed by)
        self.delete_dns_records(user=user, addresses=self.addresses.all())

        # Release all addresses associated with host.
        self.addresses.release(user=user)

        # Re-save so that it captures user for postgres log table
        try:
            self.save(user=user, add_dns=False, force_update=True)
        except DatabaseError:
            pass
        with transaction.atomic():
            super(Host, self).delete(*args, **kwargs)

    def clean(self):
        from openipam.dns.models import DnsRecord, DnsType
        from openipam.network.models import Address

        # Perform check to on hostname to not let users create a host
        if self.hostname and self.hostname != self.original_hostname:
            existing_hostname = Host.objects.filter(hostname=self.hostname).first()
            if existing_hostname:
                raise ValidationError(
                    "The hostname '%s' already exists." % (self.hostname)
                )

            existing_dns_hostname = (
                DnsRecord.objects.filter(
                    dns_type__in=[DnsType.objects.A, DnsType.objects.AAAA],
                    name=self.hostname,
                )
                .exclude(host=self)
                .first()
            )
            if existing_dns_hostname:
                raise ValidationError(
                    "DNS Records already exist for this hostname: %s. "
                    " Please contact an IPAM Administrator." % (self.hostname)
                )

        # Perform permission checks if user is attached to this instance
        # Domain permission checks if hostname has changed
        if self.hostname and self.hostname != self.original_hostname:
            domain_from_host = self.hostname.split(".")[1:]
            domain_from_host = ".".join(domain_from_host)

            valid_domain = get_objects_for_user(
                self.user,
                [
                    "dns.add_records_to_domain",
                    "dns.is_owner_domain",
                    "dns.change_domain",
                ],
                any_perm=True,
            ).filter(name=domain_from_host)
            if not valid_domain:
                raise ValidationError(
                    "Insufficient permissions to add hosts "
                    "for domain: %s. Please contact an IPAM Administrator."
                    % domain_from_host
                )

        # Pool and Network permission checks
        # Check for pool assignment and perms
        if self.address_type and self.address_type.pool:
            valid_pools = get_objects_for_user(
                self.user,
                ["network.add_records_to_pool", "network.change_pool"],
                any_perm=True,
            )
            if self.address_type.pool not in valid_pools:
                raise ValidationError(
                    "Insufficient permissions to add hosts to "
                    "the assigned pool: %s. Please contact an IPAM Administrator."
                    % self.address_type.pool
                )

        # If network defined check for address assignment and perms
        if self.network:
            valid_network = get_objects_for_user(
                self.user,
                [
                    "network.add_records_to_network",
                    "network.is_owner_network",
                    "network.change_network",
                ],
                any_perm=True,
            )
            if self.network.network not in [
                network.network for network in valid_network
            ]:
                raise ValidationError(
                    "Insufficient permissions to add hosts to "
                    "the assigned network: %s. Please contact an IPAM Administrator."
                    % self.network.network
                )

        # If IP Address defined, check validity and perms
        if self.ip_address:
            ip_address = self.ip_address

            user_pools = get_objects_for_user(
                self.user,
                ["network.add_records_to_pool", "network.change_pool"],
                any_perm=True,
            )
            user_nets = get_objects_for_user(
                self.user,
                [
                    "network.add_records_to_network",
                    "network.is_owner_network",
                    "network.change_network",
                ],
                any_perm=True,
            )

            # Make sure this is valid.
            validate_ipv46_address(ip_address)
            address = Address.objects.filter(
                Q(pool__in=user_pools)
                | Q(pool__isnull=True)
                | Q(network__in=user_nets),
                Q(leases__isnull=True)
                | Q(leases__abandoned=True)
                | Q(leases__ends__lte=timezone.now())
                | Q(leases__host=self),
                Q(host__isnull=True) | Q(host=self),
                address=ip_address,
                reserved=False,
            )
            if not address:
                raise ValidationError(
                    "The IP Address is reserved, in use, or not allowed. "
                    "Please contact an IPAM Administrator."
                )

    class Meta:
        db_table = "hosts"
        permissions = (("is_owner_host", "Is owner"),)
        default_permissions = ("add", "change", "delete", "view")
        ordering = ("hostname",)


class MacOui(models.Model):
    oui = MACAddressField(primary_key=True)
    vendor = models.TextField()

    objects = NetManager()

    def __str__(self):
        return self.oui

    class Meta:
        db_table = "mac_oui"


class Notification(models.Model):
    notification = models.DateField()

    def __str__(self):
        return "%s" % self.notification

    class Meta:
        db_table = "notifications"


class StructuredAttributeValue(models.Model):
    attribute = models.ForeignKey(
        "Attribute", db_column="aid", related_name="choices", on_delete=models.CASCADE
    )
    value = models.TextField()
    is_default = models.BooleanField(default=False)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return self.value

    class Meta:
        db_table = "structured_attribute_values"
        ordering = ("attribute__name", "value")


class StructuredAttributeToHost(models.Model):
    host = models.ForeignKey(
        "Host",
        db_column="mac",
        related_name="structured_attributes",
        on_delete=models.CASCADE,
    )
    structured_attribute_value = models.ForeignKey(
        "StructuredAttributeValue", db_column="avid", on_delete=models.CASCADE
    )
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, db_column="changed_by", on_delete=models.PROTECT
    )

    def __str__(self):
        return "%s %s" % (self.host.hostname, self.structured_attribute_value)

    class Meta:
        db_table = "structured_attributes_to_hosts"


class OUI(models.Model):
    # oui = MACAddressField()
    # mask = MACAddressField()
    start = MACAddressField()
    stop = MACAddressField()
    shortname = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "%s: %s" % (self.pk, self.shortname)

    class Meta:
        db_table = "ouis"


# Host signals
pre_delete.connect(remove_obj_perms_connected_with_user, sender=Host)
