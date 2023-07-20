"""DNS API Views."""

from openipam.dns.models import DnsRecord, Domain
from ..serializers.dns import DNSSerializer, DomainSerializer
from rest_framework import permissions
from .base import APIModelViewSet
from ..filters.dns import DnsFilter, DomainFilter


class DnsViewSet(APIModelViewSet):
    """API endpoint that allows dns records to be viewed or edited."""

    queryset = DnsRecord.objects.select_related("ip_content", "dns_type", "host").all()
    serializer_class = DNSSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterFields = ["name", "ip_content", "text_content", "dns_type"]
    filterClass = DnsFilter


class DomainViewSet(APIModelViewSet):
    queryset = Domain.objects.select_related().all()
    serializer_class = DomainSerializer
    filterFields = ("name", "username")
    filter_class = DomainFilter
