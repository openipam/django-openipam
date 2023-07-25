from openipam.dns.models import DnsRecord, Domain, DnsType
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


class DNSSerializer(serializers.ModelSerializer):
    """DNS serializer."""
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
        fields = ("name", "content", "dns_type", "ttl", "host", "id", "url")
        # extra_kwargs = {"url": {"view_name": "api_dns_view", "lookup_field": "pk"}}


class DNSCreateSerializer(serializers.ModelSerializer):
    """DNS create serializer."""
    text_content = serializers.CharField(required=False, allow_blank=True)
    ip_content = serializers.CharField(required=False, allow_blank=True)

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
        try:
            data["content"] = data["ip_content"]
            data.pop("ip_content")
        except KeyError:
            data["content"] = data["text_content"]
            data.pop("text_content")
        data["dns_type"] = DnsType.objects.filter(name__iexact=data["dns_type"]).first()
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
                    "The Dns Type selected is not valid.  Please enter a valid type " +
                    "(https://en.wikipedia.org/wiki/List_of_DNS_record_types)"
                )
            try:
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
        fields = ("name", "content", "text_content", "ip_content", "dns_type", "ttl", "host")


class DomainSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    class Meta:
        model = Domain
        fields = "__all__"


class DomainCreateSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    def save(self):
        data = self.validated_data.copy()
        data["changed_by"] = self.context["request"].user
        self.instance = Domain(**data)
        self.instance.save()
        return self.instance

    class Meta:
        model = Domain
        fields = "__all__"
