from django.contrib.auth.models import update_last_login

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework import pagination

from rest_framework_jwt.views import ObtainJSONWebToken, jwt_response_payload_handler

from openipam.conf.ipam_settings import CONFIG

from django.utils import timezone
from django.db.models import Q
from django.core import serializers

from openipam.user.models import User
from openipam.hosts.models import Host
from openipam.dns.models import DnsRecord
from openipam.network.models import Lease, Network, Address

from functools import reduce
import datetime
import operator


class UserAuthenticated(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = {
            "detail": "User is authenticated",
            "username": request.user.username,
            "is_superuser": request.user.is_superuser,
            "is_ipamadmin": request.user.is_ipamadmin,
        }
        return Response(data, status=status.HTTP_200_OK)


class APIPagination(pagination.LimitOffsetPagination):
    default_limit = 50
    limit_query_param = "limit"
    max_limit = None

    def get_limit(self, request):
        ret = pagination._positive_int(
            request.query_params.get(self.limit_query_param, self.default_limit),
            strict=False,
            cutoff=self.max_limit,
        )
        if ret == 0:
            return self.max_limit
        return ret


class APIMaxPagination(pagination.LimitOffsetPagination):
    default_limit = 50
    limit_query_param = "limit"
    max_limit = 10000

    def get_limit(self, request):
        ret = pagination._positive_int(
            request.query_params.get(self.limit_query_param, self.default_limit),
            strict=False,
            cutoff=self.max_limit,
        )
        if ret == 0:
            return self.max_limit
        return ret


class TokenAuthenticationView(ObtainJSONWebToken):
    """Implementation of ObtainAuthToken with last_login update"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get("user") or request.user
            update_last_login(None, user)
            token = serializer.object.get("token")
            response_data = jwt_response_payload_handler(token, user, request)

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


obtain_jwt_token = TokenAuthenticationView.as_view()


class OverviewStatsAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        context = {}

        wireless_networks = Network.objects.filter(
            dhcp_group__name__in=["aruba_wireless", "aruba_wireless_eastern"]
        )
        wireless_networks_available_qs = [
            Q(address__net_contained=network.network) for network in wireless_networks
        ]

        context.update(
            {
                "dynamic_hosts": Host.objects.filter(
                    pools__isnull=False, expires__gte=timezone.now()
                ).count(),
                "static_hosts": Host.objects.filter(
                    addresses__isnull=False, expires__gte=timezone.now()
                ).count(),
                "active_leases": Lease.objects.filter(ends__gte=timezone.now()).count(),
                "abandoned_leases": Lease.objects.filter(abandoned=True).count(),
                "total_networks": Network.objects.all().count(),
                "wireless_networks": wireless_networks.count(),
                "wireless_addresses_total": Address.objects.filter(
                    reduce(operator.or_, wireless_networks_available_qs)
                ).count(),
                "wireless_addresses_available": Address.objects.filter(
                    reduce(operator.or_, wireless_networks_available_qs),
                    leases__ends__lt=timezone.now(),
                ).count(),
                "dns_a_records": DnsRecord.objects.filter(
                    dns_type__name__in=["A", "AAAA"]
                ).count(),
                "dns_cname_records": DnsRecord.objects.filter(
                    dns_type__name="CNAME"
                ).count(),
                "dns_mx_records": DnsRecord.objects.filter(dns_type__name="MX").count(),
                "active_users": User.objects.filter(
                    last_login__gte=(timezone.now() - datetime.timedelta(days=365))
                ).count(),
                "user_hosts_dynamic": request.user.host_set.filter(
                    pools__isnull=False, expires__gte=timezone.now()
                ).count(),
                "user_hosts_static": request.user.host_set.filter(
                    addresses__isnull=False, expires__gte=timezone.now()
                ).count(),
                "user_dns_a": request.user.dnsrecord_set.filter(
                    dns_type__name__in=["A", "AAAA"]
                ).count(),
                "user_dns_cname": request.user.dnsrecord_set.filter(
                    dns_type__name="CNAME"
                ).count(),
                "user_dns_mx": request.user.dnsrecord_set.filter(
                    dns_type__name="MX"
                ).count(),
            }
        )
        return Response(context, status=status.HTTP_200_OK)
