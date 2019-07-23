from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete

from openipam.dns.managers import (
    DnsManager,
    DnsTypeManager,
    DomainQuerySet,
    DNSQuerySet,
)
from openipam.dns.validators import (
    validate_fqdn,
    validate_soa_content,
    validate_srv_content,
    validate_sshfp_content,
)
from openipam.user.signals import remove_obj_perms_connected_with_user

from guardian.shortcuts import get_objects_for_user

import re
import operator
from functools import reduce


class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    master = models.CharField(max_length=128, blank=True, null=True, default=None)
    last_check = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(blank=True, null=True)
    account = models.CharField(max_length=40, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey("user.User", db_column="changed_by")

    objects = DomainQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "domains"
        permissions = (
            ("is_owner_domain", "Is owner"),
            ("add_records_to_domain", "Can add records to"),
        )


class DnsRecord(models.Model):
    domain = models.ForeignKey("Domain", db_column="did", verbose_name="Domain")
    host = models.ForeignKey(
        "hosts.Host", db_column="mac", related_name="dns_records", blank=True, null=True
    )
    dns_type = models.ForeignKey(
        "DnsType",
        db_column="tid",
        verbose_name="Type",
        related_name="records",
        error_messages={"blank": "Type fields for DNS records cannot be blank."},
    )
    dns_view = models.ForeignKey(
        "DnsView", db_column="vid", verbose_name="View", blank=True, null=True
    )
    name = models.CharField(
        max_length=255,
        error_messages={"blank": "Name fields for DNS records cannot be blank."},
    )
    text_content = models.CharField(max_length=255, blank=True, null=True)
    ip_content = models.ForeignKey(
        "network.Address",
        db_column="ip_content",
        verbose_name="IP Content",
        blank=True,
        null=True,
        related_name="arecords",
    )
    ttl = models.IntegerField(default=14400, blank=True, null=True)
    priority = models.IntegerField(verbose_name="Priority", blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey("user.User", db_column="changed_by")

    objects = DnsManager.from_queryset(DNSQuerySet)()

    def __str__(self):
        return self.name

    @property
    def content(self):
        return self.ip_content if self.ip_content else self.text_content

    def clean(self):
        # Make sure these are saved as NULL to db.
        if not self.text_content:
            self.text_content = None
        if not self.ip_content:
            self.ip_content = None

        # Make sure we have text or ip content
        if not self.text_content and not self.ip_content:
            raise ValidationError(
                "Either Text Content or IP Content must exist for %s."
                % (self.name if self.name else "record",)
            )

        # But we cannot have both text and ip content
        if self.text_content and self.ip_content:
            raise ValidationError(
                "Text Content and IP Content cannot both exist for %s."
                % (self.name if self.name else "record",)
            )

        # Make sure the Hosts are assigned for valid types
        if self.dns_type.is_host_type and not self.host:
            raise ValidationError(
                "A Host needs to be assigned DNS Records of type '%s'"
                % self.dns_type.name
            )

        # Make sure PTR for desired host has the address already assigned.
        if self.dns_type.is_ptr_record:
            from openipam.network.models import Address

            host_addresses = [
                str(address.address)
                for address in Address.objects.filter(host=self.host)
            ]
            address = self.name.split(".")
            address.reverse()
            address = ".".join(address[2:])
            if address not in host_addresses:
                raise ValidationError(
                    "Invalid PTR Record.  Host %s has no address %s."
                    % (self.text_content, address)
                )

        # If these records, then they must have valid A records first, and user must have Host permission
        if self.dns_type.name in ["HINFO", "SSHFP"]:
            arecords = DnsRecord.objects.filter(
                dns_type__in=[DnsType.objects.A, DnsType.objects.AAAA],
                name=self.text_content,
            ).first()
            if not arecords:
                raise ValidationError(
                    "Invalid DNS Record.  A record for '%s' needs to exist first."
                    % self.text_content
                )

        # Run permission checks
        self.clean_permissions()

    def clean_permissions(self):
        from openipam.network.models import Address

        user = self.changed_by

        # Validate ability to add dns records
        if not self.pk and not user.has_perm("dns.add_dnsrecord"):
            raise ValidationError(
                "Invalid credentials: user %s does not have permissions"
                " to add DNS records. Please contact an IPAM administrator."
                % self.changed_by
            )

        # Validate permissions on DNS Type
        valid_dns_types = get_objects_for_user(
            user,
            ["dns.add_records_to_dnstype", "dns.change_dnstype"],
            any_perm=True,
            use_groups=True,
        )
        if self.dns_type not in valid_dns_types:
            raise ValidationError(
                "Invalid credentials: user %s does not have permissions"
                " to add '%s' records" % (user, self.dns_type.name)
            )

        valid_domains = Domain.objects.by_dns_change_perms(user).filter(
            pk=self.domain.pk
        )
        valid_addresses = Address.objects.by_dns_change_perms(user)

        # Users must either have domain permissions when except for PTRs what are being created from host saves.
        if self.dns_type.is_ptr_record and self.host.is_dirty():
            pass
        elif not valid_domains or self.domain not in valid_domains:
            raise ValidationError(
                "Invalid credentials: user %s does not have permissions"
                " to add DNS records to the domain provided. Please contact an IPAM administrator "
                "to ensure you have the proper permissions." % user
            )

        # If A or AAAA, then users must have Address / Network permission
        if self.dns_type.is_a_record and not valid_addresses.filter(
            address=self.ip_content.address
        ):
            raise ValidationError(
                "Invalid credentials: user %s does not have permissions"
                " to add DNS records to the address provided. Please contact an IPAM administrator "
                "to ensure you have the proper host and/or network permissions." % user
            )

        # If PTR, then users must have Address / Network permission
        if self.dns_type.is_ptr_record and not valid_addresses.filter(host=self.host):
            raise ValidationError(
                "Invalid credentials: user %s does not have permissions"
                " to add or modify DNS Records for Host '%s'"
                % (user, self.text_content)
            )

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

        # Clean the text_content
        try:
            self.clean_text_content()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        # Clean the dns_type
        try:
            self.clean_dns_type()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        # Clean the priority
        try:
            self.clean_priority()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    def clean_name(self):
        # Make sure name is lowercase
        self.name = self.name.lower().strip()

        # Clean name if A or AAAA record
        if self.dns_type.is_a_record:
            dns_exists = DnsRecord.objects.filter(
                name=self.name,
                dns_type__in=[DnsType.objects.A, DnsType.objects.AAAA],
                ip_content=self.ip_content,
                dns_view__isnull=True,
            ).exclude(pk=self.pk)
            if dns_exists:
                raise ValidationError(
                    {
                        "name": [
                            "Invalid name for A or AAAA record: '%s'. "
                            "Name already exists for IP '%s'."
                            % (self.name, self.ip_content)
                        ]
                    }
                )

        # Clean name if PTR record
        if self.dns_type.is_ptr_record and self.domain:
            if "in-addr.arpa" not in self.name and "ip6.arpa" not in self.name:
                raise ValidationError(
                    {"name": ["Invalid name for PTR record: %s" % self.name]}
                )
            else:
                dns_exists = DnsRecord.objects.filter(
                    name=self.name, dns_type=DnsType.objects.PTR
                ).exclude(pk=self.pk)
                if dns_exists:
                    raise ValidationError(
                        {
                            "name": [
                                "Invalid name for PTR record: %s. Name already exists."
                                % self.name
                            ]
                        }
                    )

    def clean_text_content(self):
        # Validate text content based on dns type
        # TODO: more of these need to be added
        try:
            if self.text_content:
                if self.dns_type.name in ["NS", "CNAME", "PTR", "MX"]:
                    validate_fqdn(self.text_content)

                elif self.dns_type.is_soa_record:
                    validate_soa_content(self.text_content)

                elif self.dns_type.is_srv_record:
                    validate_srv_content(self.text_content)

                elif self.dns_type.is_sshfp_record:
                    validate_sshfp_content(self.text_content)

                elif self.dns_type.is_a_record:
                    raise ValidationError(
                        "Text Content should not be assigned with A records."
                    )

                # Validate Existing Records
                dns_exists = DnsRecord.objects.filter(
                    name=self.name,
                    dns_type=self.dns_type,
                    text_content=self.text_content,
                ).exclude(pk=self.pk)
                if dns_exists:
                    raise ValidationError(
                        "DNS Record with name: '%s', type: '%s', "
                        "and content: '%s' already exists."
                        % (self.name, self.dns_type, self.text_content)
                    )

        except ValidationError as e:
            raise ValidationError({"text_content": e.messages})

    def clean_priority(self):
        error_list = []

        # Priority must exist for MX and SRV records
        if self.priority is None:
            if self.dns_type and self.dns_type.name in ["MX", "SRV"]:
                error_list.append("Priority must exist for MX and SRV records.")

                # Validation for Priority
                parsed_content = self.text_content.strip().split(" ")
                if self.dns_type.is_mx_record and len(parsed_content) != 2:
                    error_list.append(
                        "Content for MX records need to have a priority and FQDN."
                    )
                elif self.dns_type.is_srv_record and len(parsed_content) != 4:
                    error_list.append(
                        "Content for SRV records need to only have a priority, weight, port, and FQDN."
                    )

        if error_list:
            raise ValidationError({"priority": error_list})

    def clean_dns_type(self):
        error_list = []

        if self.dns_type:
            # Text content cannot exist for A records and IP must exist for A records
            if self.dns_type.is_a_record:
                if self.text_content:
                    error_list.append("Text Content must not exist for A records.")
                if not self.ip_content:
                    error_list.append("IP Content must exist for A records.")

            # Name and text content cannot be the same if its a CNAME
            if self.dns_type.is_cname_record and self.name == self.text_content:
                error_list.append(
                    "Name and Text Content cannot match for CNAME records."
                )

            if self.dns_type.is_cname_record:
                records = DnsRecord.objects.filter(
                    name=self.name, dns_type=self.dns_type
                ).exclude(pk=self.pk)
                if records:
                    error_list.append(
                        "Trying to create CNAME record while other records exist: %s"
                        % records[0].name
                    )
            # not CNAME
            else:
                records = DnsRecord.objects.filter(
                    name=self.name, dns_view=self.dns_view, dns_type_id=5
                ).exclude(pk=self.pk)
                if records:
                    error_list.append(
                        "Trying to create record while CNAME record exists:  %s"
                        % records[0].name
                    )

            if error_list:
                raise ValidationError({"dns_type": error_list})

    def set_domain_from_name(self):
        if self.name:
            names = self.name.strip().split(".")
            names_list = []
            while names:
                names_list.append(Q(name=".".join(names)))
                names.pop(0)

            if names_list:
                domain = (
                    Domain.objects.filter(reduce(operator.or_, names_list))
                    .extra(select={"length": "Length(name)"})
                    .order_by("-length")
                    .first()
                )
                if domain:
                    self.domain = domain
                else:
                    raise ValidationError(
                        {
                            "name": [
                                "Cannot create name %s: no matching domain exists"
                                % self.name
                            ]
                        }
                    )
            else:
                self.domain = None

            if not self.domain:
                raise ValidationError({"name": ["Invalid domain name: %s" % self.name]})

            if self.domain.type == "SLAVE":
                raise ValidationError(
                    {
                        "name": [
                            "Cannot create name %s: not authoritative for domain"
                            % self.name
                        ]
                    }
                )
        else:
            raise ValidationError({"name": ["Domain name cannot be blank."]})

    def set_priority(self):
        """
        Checks for priority and sets it if it exists
        """
        # Make sure that priority was set, or set it if they passed it
        match = None

        if self.dns_type.is_mx_record:  # MX
            match = re.compile(r"^([0-9]{1,3}) (.*)$").search(self.text_content)
        elif self.dns_type.is_srv_record:  # SRV
            match = re.compile(r"^([0-9]{1,3}) (\d+ \d+ .*)$").search(self.text_content)
        if match:
            # We have priority in the content
            self.priority = match.group(1)
            self.text_content = match.group(2)

    def clear_content(self):
        self.ip_content = None
        self.text_content = None

    class Meta:
        db_table = "dns_records"
        ordering = ("dns_type", "name")
        default_permissions = ("add", "change", "delete", "view")
        verbose_name = "DNS Record"


class DnsRecordMunged(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "dns_records_munged"


class DhcpDnsRecord(models.Model):
    domain = models.ForeignKey("Domain", db_column="did")
    host = models.OneToOneField("hosts.Host", db_column="name", to_field="hostname")
    ip_content = models.ForeignKey(
        "network.Address", null=True, db_column="ip_content", blank=True
    )
    ttl = models.IntegerField(default=-1, blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.host_id

    class Meta:
        db_table = "dhcp_dns_records"


class DnsType(models.Model):
    name = models.CharField(max_length=16, blank=True, unique=True)
    description = models.TextField(blank=True, null=True)
    min_permissions = models.CharField(max_length=8)  # FIXME

    objects = DnsTypeManager()

    def __str__(self):
        return "%s" % self.name

    def __getattr__(self, name):
        if name.startswith("is_") and name.endswith("_record"):

            def _is_record(abrev):
                if abrev == "a":
                    return True if self.name in ["A", "AAAA"] else False
                else:
                    return True if self.name == abrev.upper() else False

            return _is_record(name.split("_")[1])
        else:
            raise AttributeError(
                "%r object has no attribute %r" % (self.__class__, name)
            )

    @property
    def is_host_type(self):
        return True if self.name in ["A", "AAAA", "PTR", "HINFO", "SSHFP"] else False

    class Meta:
        db_table = "dns_types"
        permissions = (("add_records_to_dnstype", "Can add records to"),)
        ordering = ("name",)
        verbose_name = "DNS Type"


class DnsView(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        db_table = "dns_views"


class Supermaster(models.Model):
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True, null=True, default=None)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey("user.User", db_column="changed_by")

    def __str__(self):
        return self.ip

    class Meta:
        db_table = "supermasters"


class PdnsZoneXfer(models.Model):
    domain = models.ForeignKey("Domain")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    content = models.CharField(max_length=255)
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "pdns_zone_xfer"


class Record(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.domain_id, self.name)

    class Meta:
        managed = False
        db_table = "records"


class RecordMunged(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "%s %s" % (self.domain_id, self.name)

    class Meta:
        managed = False
        db_table = "records_munged"


# Register Signals
pre_delete.connect(remove_obj_perms_connected_with_user, sender=DnsType)
