from openipam.dns.models import DnsRecord, Domain
from rest_framework import serializers


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


class DomainSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    class Meta:
        model = Domain
        fields = "__all__"
