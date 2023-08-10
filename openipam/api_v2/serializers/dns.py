from django.db import DataError
from openipam.dns.models import DnsRecord, Domain, DnsType, DnsView, DhcpDnsRecord
from rest_framework import serializers
from guardian.shortcuts import get_objects_for_user
from django.core.exceptions import ValidationError
from openipam.dns.validators import (
    validate_fqdn,
    validate_srv_content,
    validate_soa_content,
    validate_sshfp_content,
)
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from ipaddress import IPv4Address
from guardian.models import GroupObjectPermission, UserObjectPermission
from openipam.hosts.models import Host
from django.utils import timezone


class DNSSerializer(serializers.ModelSerializer):
    """DNS serializer."""

    content = serializers.SerializerMethodField()
    dns_type = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()

    def get_content(self, obj: DnsRecord):
        # Content might be an IP address, in which case it's a foreign key
        # to an IP address object.  If it's not an IP address, it's a string.
        # Either way, str() should work.
        return str(obj.content)

    def get_dns_type(self, obj: DnsRecord):
        return obj.dns_type.name

    def get_host(self, obj):
        # Host is nullable, so we need to check for that
        return obj.host.hostname if obj.host else None

    class Meta:
        model = DnsRecord
        fields = ("name", "content", "dns_type", "ttl", "host", "id", "url")
        # extra_kwargs = {"url": {"view_name": "api_dns_view", "lookup_field": "pk"}}


class DNSCreateSerializer(serializers.ModelSerializer):
    """DNS create serializer."""

    content = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(DNSCreateSerializer, self).__init__(*args, **kwargs)

        # THIS IS STUPID!
        user = self.context["request"].user
        blank_choice = [("", "-------------")]
        dns_type_choices = get_objects_for_user(
            user,
            ["dns.add_records_to_dnstype", "dns.change_dnstype"],
            any_perm=True,
            use_groups=True,
            with_superuser=True,
        )
        self.fields["dns_type"] = serializers.ChoiceField(
            required=True,
            choices=blank_choice
            + [(dns_type.name, dns_type.name) for dns_type in dns_type_choices],
        )

    def save(self):
        is_new = True if self.instance is None else False
        data = self.validated_data.copy()
        data["record"] = self.instance
        data["user"] = self.context["request"].user
        print(f"\nDNS data: {data}")
        try:
            data["content"] = data["ip_content"]
            data.pop("ip_content")
            try:
                if data["text_content"]:
                    raise serializers.ValidationError(
                        "Cannot include both ip content and text content"
                    )
            except KeyError:
                pass
        except KeyError:
            data["content"] = data["text_content"]
            data.pop("text_content")

        data["dns_type"] = DnsType.objects.filter(name__iexact=data["dns_type"]).first()
        self.instance, create = DnsRecord.objects.add_or_update_record(**data)

        # Try to find the host
        if not self.instance.host:
            if self.instance.dns_type.name in ["A", "AAAA"]:
                lookup = {"hostname": self.instance.name}
            elif self.instance.dns_type.name == "CNAME":
                lookup = {"hostname": self.instance.content}
            elif self.instance.dns_type.name in ["TXT", "SRV"]:
                lookup = {"hostname": self.instance.content}
            try:
                host = Host.objects.filter(**lookup).first()
                if host:
                    self.instance.host = host
                    self.instance.save()
            except DataError:
                pass

        LogEntry.objects.log_action(
            user_id=self.context["request"].user.pk,
            content_type_id=ContentType.objects.get_for_model(self.instance).pk,
            object_id=self.instance.pk,
            object_repr=force_text(self.instance),
            action_flag=ADDITION if is_new else CHANGE,
            change_message="API call.",
        )
        return self.instance

    def run_validation(self, input_data):
        data = input_data.copy()
        print(f"\nvalidate data: {data}")
        if data["dns_type"]:
            dns_type = DnsType.objects.filter(name__iexact=data["dns_type"]).first()
            if not dns_type:
                raise serializers.ValidationError(
                    "The Dns Type selected is not valid.  Please enter a valid type "
                    + "(https://en.wikipedia.org/wiki/List_of_DNS_record_types)"
                )
            if dns_type.name in ["A", "AAAA"]:
                data["ip_content"] = data["content"]
            else:
                data["text_content"] = data["content"]
            data.pop("content")
            try:
                print(f"\nvalidating data: {data}")
                if data["text_content"]:
                    try:
                        if dns_type.name in ["NS", "CNAME", "PTR", "MX"]:
                            validate_fqdn(data["text_content"])

                        elif dns_type.is_soa_record:
                            validate_soa_content(data["text_content"])

                        elif dns_type.is_srv_record:
                            validate_srv_content(data["text_content"])

                        elif dns_type.is_sshfp_record:
                            validate_sshfp_content(data["text_content"])

                        elif dns_type.is_a_record:
                            raise serializers.ValidationError(
                                "Content should not be added with A records."
                            )
                    except ValidationError as e:
                        raise serializers.ValidationError({"text_content": e.messages})
            except KeyError:
                try:
                    if dns_type.name in ["NS", "CNAME", "PTR", "MX"]:
                        validate_fqdn(data["ip_content"])

                    elif dns_type.is_soa_record:
                        validate_soa_content(data["ip_content"])

                    elif dns_type.is_srv_record:
                        validate_srv_content(data["ip_content"])

                    elif dns_type.is_sshfp_record:
                        validate_sshfp_content(data["ip_content"])

                    elif dns_type.is_a_record:
                        raise serializers.ValidationError(
                            "Content should not be added with A records."
                        )
                except ValidationError as e:
                    raise serializers.ValidationError({"ip_content": e.messages})
        return data

    class Meta:
        model = DnsRecord
        fields = (
            "name",
            "content",
            "dns_type",
            "ttl",
            "host",
        )


class DomainSerializer(serializers.ModelSerializer):
    user_permissions_queryset = UserObjectPermission.objects.select_related(
        "user", "permission"
    ).filter(content_type__model=Domain._meta.model_name)
    group_permissions_queryset = GroupObjectPermission.objects.select_related(
        "group", "permission"
    ).filter(content_type__model=Domain._meta.model_name)

    changed_by = serializers.SerializerMethodField()
    user_perms = serializers.SerializerMethodField()
    group_perms = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    record_count = serializers.SerializerMethodField()

    def get_record_count(self, obj):
        # If the object has an annotation for record_count, use that.
        # Otherwise, fall back to hitting the database again.
        return getattr(obj, "record_count", obj.dnsrecord_set.count())

    def get_records(self, obj):
        """Return a url to the records for this domain."""
        return self.context["request"].build_absolute_uri(
            f"/api/v2/domains/{obj.name}/records/"
        )

    def get_user_perms(self, obj):
        perms = self.user_permissions_queryset.filter(object_pk=obj.pk)
        by_user = {}
        # Construct a dict of username -> list of permissions
        # Generally, there should probably only be one permission per
        # user, but we're not just assuming that.
        for perm in perms:
            if perm.user.username not in by_user:
                by_user[perm.user.username] = []
            by_user[perm.user.username].append(perm.permission.codename)
        return by_user

    def get_group_perms(self, obj):
        perms = self.group_permissions_queryset.filter(object_pk=obj.pk)
        by_group = {}
        # Construct a dict of group name -> list of permissions
        # Generally, there should probably only be one permission per
        # group, but we're not just assuming that.
        for perm in perms:
            if perm.group.name not in by_group:
                by_group[perm.group.name] = []
            by_group[perm.group.name].append(perm.permission.codename)
        return by_group

    def get_changed_by(self, obj):
        # Usernames are unique, and much more useful than IDs
        return obj.changed_by.username

    class Meta:
        model = Domain
        fields = "__all__"
        read_only_fields = [
            "id",
            "changed",
            "changed_by",
            "user_perms",
            "group_perms",
        ]
        extra_kwargs = {
            "url": {"lookup_field": "name"},
        }


class DomainCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, validators=[validate_fqdn])
    master = serializers.CharField(required=False, default=None)
    description = serializers.CharField(required=False, default="")
    type = serializers.ChoiceField(
        required=False,
        choices=[("SLAVE", "SLAVE"), ("NATIVE", "NATIVE")],
        default="NATIVE",
    )
    notified_serial = serializers.IntegerField(required=False, default=None)
    account = serializers.CharField(max_length=40, required=False, default=None)

    def validate(self, data):
        if data["type"] == "SLAVE":
            # This is based on current data in my copy of the database.
            # If this is wrong, let me know.
            if not data["master"] or data["master"] == "":
                raise serializers.ValidationError(
                    "Master server must be specified for slave domains."
                )
        elif data["master"] == "":
            data["master"] = None
        elif data["master"] is not None:
            # This is based on current data in my copy of the database.
            # If this is wrong, let me know.
            raise serializers.ValidationError(
                "Master server must not be specified for non-slave domains."
            )
        return data

    def save(self):
        """Save the domain."""
        # Set the changed_by field to the current user, and the changed field
        # to the current time
        self.validated_data["changed_by"] = self.context["request"].user
        self.validated_data["changed"] = timezone.now()
        # Call back to the superclass to do the actual saving
        return super().save()

    class Meta:
        model = Domain
        fields = [
            "name",
            "master",
            "description",
            "type",
            "notified_serial",
            "account",
        ]


class DnsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DnsType
        fields = "__all__"


class DnsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DnsView
        fields = "__all__"


class IPv4AddressSerializer(serializers.Serializer):
    class Meta:
        model = IPv4Address
        fields = "__all__"


class DhcpDnsRecordSerializer(serializers.ModelSerializer):
    ip_content = serializers.SerializerMethodField()
    domain = serializers.SerializerMethodField()

    def get_domain(self, obj):
        return str(obj.domain.name)

    def get_ip_content(self, obj):
        return str(obj.ip_content.address)

    class Meta:
        model = DhcpDnsRecord
        fields = ["host", "ttl", "domain", "changed", "ip_content"]
