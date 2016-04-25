from django.shortcuts import render
from django.db.models.aggregates import Count
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView

from datetime import timedelta

from openipam.hosts.models import Host, GulRecentArpBymac, GulRecentArpByaddress
from openipam.network.models import Network, NetworkRange, AddressType

from guardian.models import UserObjectPermission, GroupObjectPermission

from braces.views import GroupRequiredMixin

import qsstats

import requests
import operator


class DashboardView(GroupRequiredMixin, TemplateView):
    group_required = 'ipam_admins'
    template_name = 'report/dashboard.html'


class LeaseUsageView(GroupRequiredMixin, TemplateView):
    group_required = 'ipam_admins'
    template_name = 'report/lease_usage.html'


class WeatherMapView(GroupRequiredMixin, TemplateView):
    group_required = 'ipam_admins'
    template_name = 'report/weather_map.html'

    def get_context_data(self, **kwargs):
        context = super(WeatherMapView, self).get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', None)
        context['is_popup'] = True if popup else False
        return context


class DisabledHostsView(GroupRequiredMixin, TemplateView):
    group_required = 'ipam_admins'
    template_name = 'report/disabled.html'

    def get_context_data(self, **kwargs):
        context = super(DisabledHostsView, self).get_context_data(**kwargs)
        hardcoded = (
            GulRecentArpBymac.objects
                .select_related('host')
                .filter(
                    host__disabled_host__isnull=False,
                    stopstamp__gt=timezone.now() - timedelta(minutes=10),
                )
                .exclude(host__leases__ends__lt=timezone.now())
                .extra(where=["NOT (gul_recent_arp_bymac.address <<= '172.16.0.0/16' OR gul_recent_arp_bymac.address <<= '172.18.0.0/16')"])
        )
        context['hardcoded'] = hardcoded
        return context


class ServerHostsView(GroupRequiredMixin, TemplateView):
    group_required = 'ipam_admins'
    template_name = 'report/server_hosts.html'
