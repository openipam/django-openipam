"""Miscellaneous views that don't really fit anywhere else."""

from rest_framework import status, viewsets as lib_viewsets
from rest_framework.views import APIView
from ..serializers.misc import AttributeSerializer
from openipam.hosts.models import Attribute, StructuredAttributeValue
from django.db.models import Prefetch
from openipam.network.models import Network, Lease, Address
from openipam.hosts.models import Host
from django.utils import timezone
from openipam.dns.models import DnsRecord
from functools import reduce
import operator
from datetime import timedelta
from django.db.models import Q
from rest_framework.response import Response
from collections import OrderedDict
from django.contrib.auth import get_user_model

User = get_user_model()


class AttributeViewSet(lib_viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows attributes to be viewed or edited."""

    queryset = (
        Attribute.objects.select_related("changed_by")
        .prefetch_related(
            Prefetch(
                "choices",
                queryset=StructuredAttributeValue.objects.select_related("changed_by"),
            )
        )
        .all()
    )
    serializer_class = AttributeSerializer


class DashboardAPIView(APIView):
    def get(self, request, format=None, **kwargs):
        wireless_networks = Network.objects.filter(dhcp_group__name__in=["aruba_wireless", "aruba_wireless_eastern"])
        wireless_networks_available_qs = [Q(address__net_contained=network.network) for network in wireless_networks]

        data = (
            (
                "Static Hosts",
                "%s" % Host.objects.filter(addresses__isnull=False, expires__gte=timezone.now()).count(),
            ),
            (
                "Dynamic Hosts",
                "%s" % Host.objects.filter(pools__isnull=False, expires__gte=timezone.now()).count(),
            ),
            (
                "Active Leases",
                "%s" % Lease.objects.filter(ends__gte=timezone.now()).count(),
            ),
            ("Abandoned Leases", "%s" % Lease.objects.filter(abandoned=True).count()),
            (
                "Networks: (Total / Wireless)",
                "%s / %s" % (Network.objects.all().count(), wireless_networks.count()),
            ),
            (
                "Available Wireless Addresses",
                Address.objects.filter(
                    reduce(operator.or_, wireless_networks_available_qs),
                    leases__ends__lt=timezone.now(),
                ).count(),
            ),
            (
                "DNS A Records",
                DnsRecord.objects.filter(dns_type__name__in=["A", "AAAA"]).count(),
            ),
            (
                "DNS CNAME Records",
                DnsRecord.objects.filter(dns_type__name="CNAME").count(),
            ),
            ("DNS MX Records", DnsRecord.objects.filter(dns_type__name="MX").count()),
            (
                "Active Users Within 1 Year",
                User.objects.filter(last_login__gte=(timezone.now() - timedelta(days=365))).count(),
            ),
        )

        data = OrderedDict(data)

        return Response(data, status=status.HTTP_200_OK)
