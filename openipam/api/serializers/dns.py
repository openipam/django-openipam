from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from openipam.dns.models import Domain, DnsRecord, DnsType
from openipam.dns.validators import (
    validate_fqdn,
    validate_srv_content,
    validate_soa_content,
    validate_sshfp_content,
)

from guardian.shortcuts import get_objects_for_user


class DomainNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ("name",)


class DomainSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    class Meta:
        model = Domain
        fields = "__all__"


class DnsDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DnsRecord
        fields = ("id",)
        read_only_fields = ("id",)


class DnsListDetailSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    dns_type = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()

    def get_content(self, obj):
        return "%s" % obj.content

    def get_dns_type(self, obj):
        return "%s" % obj.dns_type.name

    def get_host(self, obj):
        return "%s" % obj.host

    class Meta:
        model = DnsRecord
        fields = ("url", "id", "name", "content", "dns_type", "ttl", "host")
        extra_kwargs = {"url": {"view_name": "api_dns_view", "lookup_field": "pk"}}


class DnsCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super(DnsCreateSerializer, self).__init__(*args, **kwargs)

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
            choices=blank_choice + [(dns_type.name, dns_type.name) for dns_type in dns_type_choices],
        )

    def save(self):
        is_new = True if self.instance is None else False
        data = self.validated_data.copy()
        data["record"] = self.instance
        data["user"] = self.context["request"].user
        self.instance, create = DnsRecord.objects.add_or_update_record(**data)

        LogEntry.objects.log_action(
            user_id=self.context["request"].user.pk,
            content_type_id=ContentType.objects.get_for_model(self.instance).pk,
            object_id=self.instance.pk,
            object_repr=force_text(self.instance),
            action_flag=ADDITION if is_new else CHANGE,
            change_message="API call.",
        )
        return self.instance

    def validate(self, data):
        if data["dns_type"]:
            dns_type = DnsType.objects.filter(name__iexact=data["dns_type"]).first()

            if not dns_type:
                raise serializers.ValidationError(
                    "The Dns Type selected is not valid.  Please enter a valid type "
                    + "(https://en.wikipedia.org/wiki/List_of_DNS_record_types)"
                )

            if data["content"]:
                try:
                    if dns_type.name in ["NS", "CNAME", "PTR", "MX"]:
                        validate_fqdn(data["content"])

                    elif dns_type.is_soa_record:
                        validate_soa_content(data["content"])

                    elif dns_type.is_srv_record:
                        validate_srv_content(data["content"])

                    elif dns_type.is_sshfp_record:
                        validate_sshfp_content(data["content"])

                    elif dns_type.is_a_record:
                        raise serializers.ValidationError("Content should not be added with A records.")
                except ValidationError as e:
                    raise serializers.ValidationError({"content": e.messages})

        return data

    def validate_name(self, value):
        if value:
            try:
                validate_fqdn(value)
            except ValidationError:
                raise serializers.ValidationError("The Dns Name is not fully qualified domain name.  Please try again.")

    class Meta:
        model = DnsRecord
        fields = ("name", "dns_type", "content", "ttl")
