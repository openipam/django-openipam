from django.shortcuts import render
from django.db.models.aggregates import Count
from django.conf import settings
from django.views.decorators.cache import cache_page

from openipam.hosts.models import Host
from openipam.network.models import Network

import qsstats

import requests

import itertools


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
    return render(request, 'usu/overview.html', context)


def lease_usage(request):
    wifi_networks = Network.objects.filter(network__net_contained='144.39.128.0/17')
    charts = []

    # var used = graphite.metric("diffSeries(ipam.leases.129-123-240-0_20.dynamic,ipam.leases.129-123-240-0_20.available)");

    for network in wifi_networks:
        charts.append(str(network.network).replace('.', '-').replace('/', '_'))

    data = {
        'charts': charts
    }

    return render(request, 'usu/lease_utilization.html', data)


#@cache_page(60)
def leases_available(request):
    return render(request, 'usu/leases_available.html', {'is_popup': True})


def weather_map(request):
    return render(request, 'usu/weather_map.html', {'is_popup': True})
