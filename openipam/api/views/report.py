from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import (
    TemplateHTMLRenderer,
    JSONRenderer,
    BrowsableAPIRenderer,
)
from rest_framework.views import APIView

from rest_framework_csv.renderers import CSVRenderer
from rest_framework.exceptions import ParseError, ValidationError

from django.db import connection
from django.db.models.aggregates import Count
from django.contrib.auth.models import Permission
from django.apps import apps
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from openipam.hosts.models import Host, Attribute
from openipam.network.models import Network, Lease, Address
from openipam.dns.models import DnsRecord
from openipam.conf.ipam_settings import CONFIG

from functools import reduce

import qsstats

import operator

from datetime import timedelta

import dateutil.parser

User = get_user_model()


class StatsAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request, format=None, **kwargs):
        app = request.GET.get("app")
        model = request.GET.get("model")
        column = request.GET.get("column")
        start = request.GET.get("start")
        end = request.GET.get("end")

        model_klass = apps.get_model(app_label=app, model_name=model)
        queryset = model_klass.objects.all()
        qs_stats = qsstats.QuerySetStats(queryset, column, aggregate=Count("pk"))

        time_series = []
        if start and end:
            try:
                start = dateutil.parser.parse(start)
                end = dateutil.parser.parse(end)
            except ValueError:
                raise ParseError("'start' and 'end' must be ISO date strings")
            if start >= end:
                raise ValidationError("'start' must be less than 'end'")
            if start - end > timedelta(days=31):
                raise ValidationError(
                    "'start' and 'end' must be less than or equal to 31 days apart"
                )
            time_series = qs_stats.time_series(start, end)

        xdata = (
            ["Today", "This Week", "This Month"]
            if not (start and end)
            else [int(x[0].timestamp()) for x in time_series]
        )
        ydata = (
            [qs_stats.this_day(), qs_stats.this_week(), qs_stats.this_month()]
            if not (start and end)
            else [x[1] for x in time_series]
        )

        extra_serie1 = {
            "tooltip": {
                "y_start": "",
                "y_end": " %s" % model_klass._meta.verbose_name_plural.title(),
            }
        }
        chartdata = {"x": xdata, "name1": "Hosts", "y1": ydata, "extra1": extra_serie1}
        charttype = "discreteBarChart"
        chartcontainer = "%s_stats" % model.lower()
        context = {
            "charttype": charttype,
            "chartdata": chartdata,
            "chartcontainer": chartcontainer,
            "extra": {
                "x_is_date": False,
                "x_axis_format": "",
                "tag_script_js": True,
                "jquery_on_ready": False,
            },
        }

        return Response(context, template_name="api/web/ipam_stats.html")


class DashboardAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer)

    def get(self, request, format=None, **kwargs):
        wireless_networks = Network.objects.filter(
            dhcp_group__name__in=["aruba_wireless", "aruba_wireless_eastern"]
        )
        wireless_networks_available_qs = [
            Q(address__net_contained=network.network) for network in wireless_networks
        ]

        data = (
            {
                "name": "All Hosts",
                "count": Host.objects.all().count(),
                "tip": "All hosts in openIPAM.",
            },
            {
                "name": "Expired Hosts",
                "count": Host.objects.filter(expires__lte=timezone.now()).count(),
                "tip": "All hosts who's expiry date is before today's date.",
            },
            {
                "name": "Static Hosts",
                "count": Host.objects.filter(
                    addresses__isnull=False, expires__gte=timezone.now()
                ).count(),
                "tip": "Static hosts which are not expired.",
            },
            {
                "name": "Dynamic Hosts",
                "count": Host.objects.filter(
                    pools__isnull=True, expires__gte=timezone.now()
                ).count(),
                "tip": "Dynamic hosts which are not expired.",
            },
            {
                "name": "Active Leases",
                "count": Lease.objects.filter(ends__gte=timezone.now()).count(),
                "tip": "All leases who end in the future.",
            },
            {
                "name": "Abandoned Leases",
                "count": Lease.objects.filter(abandoned=True).count(),
                "tip": "Leases that have been abandoned.",
            },
            {
                "name": "Networks: (Total / Wireless)",
                "count": f"{Network.objects.all().count()} / {wireless_networks.count()}",
                "tip": "A total of all networks / wireless networks.",
            },
            {
                "name": "Available Wireless Addresses",
                "count": Address.objects.filter(
                    reduce(operator.or_, wireless_networks_available_qs),
                    leases__ends__lt=timezone.now(),
                ).count(),
                "tip": "A total of wireless addresses available.",
            },
            {
                "name": "DNS A Records",
                "count": DnsRecord.objects.filter(
                    dns_type__name__in=["A", "AAAA"]
                ).count(),
                "tip": "Total of all A records.",
            },
            {
                "name": "DNS CNAME Records",
                "count": DnsRecord.objects.filter(dns_type__name="CNAME").count(),
                "tip": "Total of all CNAME records.",
            },
            {
                "name": "DNS MX Records",
                "count": DnsRecord.objects.filter(dns_type__name="MX").count(),
                "tip": "Total of all MX records.",
            },
            {
                "name": "Active Users Within 1 Year",
                "count": User.objects.filter(
                    last_login__gte=(timezone.now() - timedelta(days=365))
                ).count(),
                "tip": "Active Users within the last year.",
            },
        )

        return Response(data, status=status.HTTP_200_OK)


class ServerHostCSVRenderer(CSVRenderer):
    header = [
        "hostname",
        "mac",
        "description",
        "addresses",
        "user_owners",
        "group_owners",
        "nac_profiles",
    ]


class ServerHostView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, ServerHostCSVRenderer)

    def get(self, request, format=None, **kwargs):
        nac_profile_attribute = Attribute.objects.get(name="nac-profile")
        host_owner_permission = Permission.objects.get(codename="is_owner_host")

        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT hosts.hostname AS hostname,
                   hosts.mac AS mac,
                   hosts.description AS description,
                   STRING_AGG(DISTINCT((SELECT CAST(addresses.address AS VARCHAR))), ', ') AS addresses,
                   STRING_AGG(DISTINCT(users.username), ', ') AS users,
                   STRING_AGG(DISTINCT(auth_group.name), ', ') AS groups,
                   STRING_AGG(DISTINCT(host_attr_vals.value), ', ') AS nac_profiles
            FROM hosts
                JOIN structured_attributes_to_hosts AS host_attrs ON hosts.mac = host_attrs.mac
                JOIN structured_attribute_values AS host_attr_vals ON host_attrs.avid = host_attr_vals.id
                LEFT JOIN guardian_userobjectpermission AS uop ON uop.object_pk=(SELECT CAST(hosts.mac AS VARCHAR)) AND uop.permission_id = %s
                LEFT JOIN guardian_groupobjectpermission AS gop ON gop.object_pk=(SELECT CAST(hosts.mac AS VARCHAR)) AND gop.permission_id = %s
                LEFT JOIN addresses ON hosts.mac = addresses.mac
                LEFT JOIN users ON uop.user_id = users.id
                LEFT JOIN auth_group ON gop.group_id = auth_group.id
            WHERE host_attr_vals.aid = %s
            AND host_attr_vals.value LIKE %s || '%%'
            GROUP BY hosts.mac, hosts.hostname, hosts.description
            """,
            (
                host_owner_permission.id,
                host_owner_permission.id,
                nac_profile_attribute.id,
                CONFIG.get("NAC_PROFILE_IS_SERVER_PREFIX"),
            ),
        )

        data = [
            dict(zip([col[0] for col in cursor.description], row))
            for row in cursor.fetchall()
        ]

        if request.accepted_renderer.format == "json":
            return Response({"data": data}, status=status.HTTP_200_OK)
        else:
            return Response(data, status=status.HTTP_200_OK)
