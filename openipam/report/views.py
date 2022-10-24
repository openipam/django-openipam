from django.utils import timezone
from django.db.models import Q
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

from datetime import timedelta
from openipam.conf.ipam_settings import CONFIG_DEFAULTS

from openipam.hosts.models import GulRecentArpBymac, Host
from openipam.network.models import Address, Lease, Network
from openipam.dns.models import DnsRecord

from functools import reduce


from braces.views import GroupRequiredMixin

import operator

User = get_user_model()


class IpamStatsView(TemplateView):
    template_name = "report/ipam_stats.html"

    def get_context_data(self, **kwargs):
        context = super(IpamStatsView, self).get_context_data(**kwargs)

        context["dynamic_hosts"] = Host.objects.filter(
            pools__isnull=False, expires__gte=timezone.now()
        ).count()
        context["static_hosts"] = Host.objects.filter(
            addresses__isnull=False, expires__gte=timezone.now()
        ).count()
        context["active_leases"] = Lease.objects.filter(
            ends__gte=timezone.now()
        ).count()
        context["abandoned_leases"] = Lease.objects.filter(abandoned=True).count()
        context["total_networks"] = Network.objects.all().count()
        wireless_networks = Network.objects.filter(
            dhcp_group__name__in=["aruba_wireless", "aruba_wireless_eastern"]
        )
        context["wireless_networks"] = wireless_networks.count()
        wireless_networks_available_qs = [
            Q(address__net_contained=network.network) for network in wireless_networks
        ]
        context["wireless_addresses_total"] = Address.objects.filter(
            reduce(operator.or_, wireless_networks_available_qs)
        ).count()
        context["wireless_addresses_available"] = Address.objects.filter(
            reduce(operator.or_, wireless_networks_available_qs),
            leases__ends__lt=timezone.now(),
        ).count()
        context["dns_a_records"] = DnsRecord.objects.filter(
            dns_type__name__in=["A", "AAAA"]
        ).count()
        context["dns_cname_records"] = DnsRecord.objects.filter(
            dns_type__name="CNAME"
        ).count()
        context["dns_mx_records"] = DnsRecord.objects.filter(
            dns_type__name="MX"
        ).count()
        context["active_users"] = User.objects.filter(
            last_login__gte=(timezone.now() - timedelta(days=365))
        ).count()

        return context


class DisabledHostsView(GroupRequiredMixin, TemplateView):
    group_required = "ipam_admins"
    template_name = "report/disabled.html"

    def get_context_data(self, **kwargs):
        context = super(DisabledHostsView, self).get_context_data(**kwargs)

        hardcoded = (
            GulRecentArpBymac.objects.select_related("host")
            .filter(
                # host__disabled_host__isnull=False,
                stopstamp__gt=timezone.now()
                - timedelta(minutes=10)
            )
            .exclude(host__leases__ends__lt=timezone.now())
            .extra(
                where=[
                    #    "NOT (gul_recent_arp_bymac.address <<= '172.16.0.0/16' OR gul_recent_arp_bymac.address <<= '172.18.0.0/16')",
                    "gul_recent_arp_bymac.mac IN (SELECT mac from disabled)",
                ]
            )
        )

        context["hardcoded"] = hardcoded
        return context


class ExposedHostsView(GroupRequiredMixin, TemplateView):
    group_required = "ipam_admins"
    template_name = "report/exposed_hosts.html"


class HostDNSView(GroupRequiredMixin, TemplateView):
    group_required = "ipam_admins"
    template_name = "report/host_dns.html"

    def get_context_data(self, **kwargs):
        context = super(HostDNSView, self).get_context_data(**kwargs)
        hosts = Host.objects.filter(
            dns_records__isnull=True,
            addresses__isnull=False,
            expires__gte=timezone.now(),
        )
        context["hosts"] = hosts
        return context


class PTRDNSView(GroupRequiredMixin, TemplateView):
    group_required = "ipam_admins"
    template_name = "report/ptr_dns.html"

    def get_context_data(self, **kwargs):
        context = super(PTRDNSView, self).get_context_data(**kwargs)

        rogue_ptrs = DnsRecord.objects.raw(
            r"""
            SELECT d.*, a.address as address, d3.name as arecord, a.mac as arecord_host
            FROM dns_records AS d
                LEFT JOIN addresses AS a ON (
                    regexp_replace(d.name, '([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)..*', E'\\4.\\3.\\2.\\1')::inet = a.address
                )
                LEFT JOIN dns_records AS d2 ON (
                    d2.name = d.text_content AND d2.ip_content IS NOT NULL
                )
                LEFT JOIN dns_records AS d3 ON (
                    a.address = d3.ip_content
                )
            WHERE d.tid = '12'
                AND d.name LIKE '%%.in-addr.arpa'
                AND d2.ip_content IS NULL

            ORDER BY d.changed DESC
                --AND d.text_content != d2.name
        """
        )

        context["rogue_ptrs"] = rogue_ptrs
        return context


class ExpiredHostsView(GroupRequiredMixin, TemplateView):
    group_required = "ipam_admins"
    template_name = "report/expired_hosts.html"

    def get_context_data(self, **kwargs):
        context = super(ExpiredHostsView, self).get_context_data(**kwargs)

        host_types = {
            "static": Host.objects.select_related("mac_history")
            .filter(
                pools__isnull=False,
                expires__lte=timezone.now()
                - timedelta(
                    weeks=CONFIG_DEFAULTS["STATIC_HOST_EXPIRY_THRESHOLD_WEEKS"]
                ),
                mac_history__host__isnull=True,
            )
            .order_by("-expires"),
            "dynamic": Host.objects.select_related("mac_history")
            .filter(
                pools__isnull=True,
                expires__lte=timezone.now()
                - timedelta(
                    weeks=CONFIG_DEFAULTS["DYNAMIC_HOST_EXPIRY_THRESHOLD_WEEKS"]
                ),
                mac_history__host__isnull=True,
            )
            .order_by("-expires"),
        }

        context["host_types"] = host_types
        context["static_mac_addrs"] = [str(host.mac) for host in host_types["static"]]
        context["dynamic_mac_addrs"] = [str(host.mac) for host in host_types["dynamic"]]

        return context
