from django.shortcuts import render
from django.db.models.aggregates import Count
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.db.models import Q

from datetime import timedelta

from openipam.hosts.models import Host, GulRecentArpBymac, GulRecentArpByaddress
from openipam.network.models import Network, NetworkRange, AddressType

import qsstats

import requests
import operator


def overview(request):

    hosts = Host.objects.all()
    hosts_stats = qsstats.QuerySetStats(hosts, 'changed', aggregate=Count('mac'))
    #users = User.objects.all()
    #users_stats = qsstats.QuerySetStats(users, 'date_joined')

    xdata = ['Today', 'This Week', 'This Month']
    ydata = [hosts_stats.this_day(), hosts_stats.this_week(), hosts_stats.this_month()]

    extra_serie1 = {"tooltip": {"y_start": "", "y_end": " hosts"}}
    chartdata = {
        'x': xdata, 'name1': 'Hosts', 'y1': ydata, 'extra1': extra_serie1,
    }
    charttype = "discreteBarChart"
    chartcontainer = 'bar_container'
    context = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return render(request, 'report/dashboard.html', context)


def lease_usage(request):
    return render(request, 'report/lease_usage.html')


def leases_available(request):
    return render(request, 'report/leases_available.html', {'is_popup': True})


def weather_map(request):
    return render(request, 'report/weather_map.html')


def disabled_hosts(request):
    #queritined_nets = [net.range for net in NetworkRange.objects.filter(address_ranges__name='Quarantine')]
    #q_list = [Q(address_id__net_contained_or_equal=net) for net in queritined_nets]
    #assert False, q_list
    hardcoded = (
        GulRecentArpBymac.objects
            .select_related('host')
            .filter(
                host__disabled_host__isnull=False,
                stopstamp__gt=timezone.now() - timedelta(minutes=10),
            )
            .exclude(
                host__leases__ends__lt=timezone.now()
            )
            .extra(where=["NOT (gul_recent_arp_bymac.address <<= '172.16.0.0/16' OR gul_recent_arp_bymac.address <<= '172.18.0.0/16')"])
            #.extra(
            #    select={'end_time': 'SELECT MAX(leases.ends) FROM leases where leases.mac = gul_recent_arp_bymac.mac AND ends < %s'},
            #    select_params=(timezone.now(),)
            #).distinct()
    )

    context = {
        'hardcoded': hardcoded
    }

    return render(request, 'report/disabled.html', context)
