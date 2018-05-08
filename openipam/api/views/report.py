from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes, permission_classes

from rest_framework_csv.renderers import CSVRenderer

from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.apps import apps
from django.db.models import Q
from django.utils import timezone

from openipam.hosts.models import Host
from openipam.report.models import Ports, database as observium_db
from openipam.network.models import Network, Lease, Address
from openipam.dns.models import DnsRecord
from openipam.conf.ipam_settings import CONFIG
from openipam.conf.settings import get_buildingmap_data

from guardian.models import UserObjectPermission, GroupObjectPermission

import copy

import qsstats

import operator

from netaddr import IPNetwork

import requests

import itertools

from tempfile import TemporaryFile

from datetime import datetime, timedelta

from collections import OrderedDict

User = get_user_model()


class LeaseUsageView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (BrowsableAPIRenderer, TemplateHTMLRenderer, JSONRenderer,)

    def get(self, request, format=None, **kwargs):
        network_blocks = request.GET.get('network_blocks')
        network_tags = request.GET.get('network_tags')
        by_router = request.GET.get('by_router')
        exclude_free = request.GET.get('exclude_free')

        if network_blocks:
            show_blocks = '&'.join(['show_blocks=%s' % n for n in network_blocks.split(',')])
            url = 'https://gul.usu.edu/subnetparser.py?format=json&%s' % show_blocks
            lease_data = requests.get(url, auth=('django-openipam', 'ZEraWDJ1aSLsYmzvqhUT2ZL4z2xpA9Yt'))
        elif network_tags:
            network_tags = network_tags.split(',')
            networks = Network.objects.filter(dhcp_group__name__in=network_tags)
            show_blocks = '&'.join(['show_blocks=%s' % str(n.network) for n in networks])
            url = 'https://gul.usu.edu/subnetparser.py?format=json&%s' % show_blocks
            lease_data = requests.get(url, auth=('django-openipam', 'ZEraWDJ1aSLsYmzvqhUT2ZL4z2xpA9Yt'))
        else:
            lease_data = requests.get('https://gul.usu.edu/subnetparser.py?format=json',
                                      auth=('django-openipam', 'ZEraWDJ1aSLsYmzvqhUT2ZL4z2xpA9Yt'))

        try:
            lease_data = lease_data.json()
        except ValueError:
            return HttpResponse('Error parsing JSON from GUL', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        lease_data = sorted(lease_data, key=lambda k: (k['router'], IPNetwork(k['network'])))

        def get_ratio(available, total):
            ratio = 1
            if total != 0:
                ratio = available * 1.0 / total
            else:
                ratio = None
            return ratio

        def color(ratio):
            # Convert a number in the range [0,1] to an HTML color code
            if ratio is None:
                return '#77f'
            if ratio < 0:
                ratio = 0
            if ratio > 1:
                ratio = 1

            r = ratio * 2.0 - 1
            g = ratio * 2.0

            if r < 0.0:
                r = 0.0
            if g > 1.0:
                g = 1.0

            rgb = ((1 - r) * 255, g * 255, 0)
            color = "#%02x%02x%02x" % rgb
            return color

        if not by_router:
            for item in lease_data:
                network = IPNetwork(item['network'])
                child = item

                if 'usage' in item:
                    child['ratio'] = get_ratio(item['usage']['available'], item['usage']['dynamic'])
                    child['utilized'] = int((1 - child['ratio']) * 100) if child['ratio'] is not None else 0
                else:
                    child['ratio'] = 1
                    child['utilized'] = 0

                if 'ratio' in item:
                    child['style'] = color(child['ratio'])
                else:
                    child['style'] = '#77f'

                child['size'] = network.size
                if network.prefixlen >= 28:
                    child['size_width'] = 50
                else:
                    child['size_width'] = (32 - 4 - network.prefixlen) ** 1.5 * 20 + 50

            lease_data = sorted(lease_data, key=lambda x: float(x['ratio']) if x['ratio'] is not None else 1.1)

            if request.accepted_renderer.format == 'html':
                context = {
                    'lease_data': lease_data,
                    'excluded_keys': ['style']
                }
                return Response(context, template_name='api/web/lease_usage.html')
            else:
                return Response(lease_data, status=status.HTTP_200_OK, template_name='api/web/lease_usage.html')

        grouped_lease_data = {
            'name': 'routers',
            'children': [],
            'style': '#000033'
        }

        routers_css = [
            {'router': 'ser.gw.usu.edu', 'color': '#00A7C0', },
            {'router': 'wireless.gw.usu.edu', 'color': '#507780', },
            {'router': 'main.gw.usu.edu', 'color': '#E85649', },
            {'router': 'ed.gw.usu.edu', 'color': '#E09A25', },
            {'router': 'rpark.gw.usu.edu', 'color': '#FFE11A', },
            {'router': 'spectrum.gw.usu.edu', 'color': '#9cf', },
            {'router': 'hsg-av.gw.usu.edu', 'color': '#F22738', },
            {'router': 'hsg-ser.gw.usu.edu', 'color': '#F22738', },
            {'router': 'hsg-llc.gw.usu.edu', 'color': '#F22738', },
            {'router': 'airport.gw.usu.edu', 'color': '#9f9', },
            {'router': 'dmz-a.gw.usu.edu', 'color': '#70a7b0', },
            {'router': 'dmz-b.gw.usu.edu', 'color': '#70a7b0', },
            # {'router': '.gw.usu.edu', 'color': '#9f9', },
            {'router': 'aste.gw.usu.edu', 'color': '#f99', },
            {'router': 'brigham.gw.usu.edu', 'color': '#9f9', },
            {'router': 'ceu.gw.usu.edu', 'color': '#99f', },
            {'router': 'blanding.gw.usu.edu', 'color': '#66d', },
            {'router': 'UEN', 'color': '#f64', },
            {'router': 'multiple', 'color': '#999', },
        ]

        for key, group in itertools.groupby(lease_data, lambda item: item['router']):

            if exclude_free and key is None:
                continue

            router = {
                'name': key.replace('.gw.usu.edu', '') if key is not None else 'FREE',
                'children': [],
            }

            # if key is not None:
            #     _color = filter(lambda x: x['router'] == key, routers_css)
            #     if _color:
            #         router['style'] = _color[0]['color']
            # else:
            #     router['style'] = '#00ff00'

            # second_child = {
            #     'name': 'smaller',
            #     'children': [],
            #     'style': '#77f',
            #     'ratio': 1
            # }
            # third_child = {
            #     'name': 'smaller',
            #     'children': [],
            #     'style': '#77f',
            #     'ratio': 1
            # }
            for item in group:
                network = IPNetwork(item['network'])
                child = item

                # else:
                #    child['style'] = '#00ff00'

                if 'usage' in item:
                    child['ratio'] = get_ratio(item['usage']['available'], item['usage']['dynamic'])
                else:
                    child['ratio'] = 1

                # if key is not None:
                if 'ratio' in item:
                    child['style'] = color(child['ratio'])
                else:
                    child['style'] = '#77f'

                child['name'] = item['network']
                child['desc'] = item['portdesc']
                child['size'] = network.size
                child['value'] = network.size if network.size > 256 else 256
                del child['router']

                # if network.prefixlen > 28:
                #     third_child['children'].append(child)
                # elif network.prefixlen > 24:
                #     second_child['children'].append(child)
                # else:
                router['children'].append(child)

            # if third_child['children']:
            #     ratio_min = min([child['ratio'] for child in third_child['children'] if child['ratio'] is not None])
            #     third_child['style'] = color(ratio_min)
            #     second_child['children'].append(third_child)

            # if second_child['children']:
            #     ratio_min = min([child['ratio'] for child in second_child['children'] if child['ratio'] is not None])
            #     # if router['name'] == 'FREE':
            #     #     for child in second_child['children']:
            #     #         if child['ratio'] < 1:
            #     #             print child
            #     second_child['style'] = color(ratio_min)

            #     router['children'].append(second_child)

            grouped_lease_data['children'].append(router)

        return Response(grouped_lease_data, status=status.HTTP_200_OK, template_name='api/web/lease_usage.html')


class LeaseGraphView(APIView):
    permission_classes = (AllowAny,)
    # renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, network, format=None, **kwargs):
        parsed_network = network.replace('/', '_').replace('.', '-')
        params = {
            'width': '700',
            'height': '350',
            '_salt': '1414518442.099',
            'areaMode': 'stacked',
            'from': '-1weeks',
            'bgcolor': '000000',
            'fgcolor': 'FFFFFF',
            'target': [
                'color(aliasByMetric(ipam.leases.%s.reserved),"purple")' % parsed_network,
                'color(aliasByMetric(ipam.leases.%s.static),"orange")' % parsed_network,
                'color(aliasByMetric(ipam.leases.%s.abandoned),"red")' % parsed_network,
                'color(aliasByMetric(ipam.leases.%s.leased),"yellow")' % parsed_network,
                'color(aliasByMetric(ipam.leases.%s.expired),"green")' % parsed_network,
                'color(aliasByMetric(ipam.leases.%s.unleased),"blue")' % parsed_network,
            ]
        }
        req = requests.get(
            'http://graphite.ser321.usu.edu:8190/render/',
            params=params,
            stream=True)

        if req.status_code == 200:
            with TemporaryFile() as f:
                for chunk in req.iter_content():
                    f.write(chunk)
                f.seek(0)
                return HttpResponse(f, content_type='image/png')
        else:
            return HttpResponse(req.reason, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WeatherMapView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,)

    def get(self, request, format=None, **kwargs):
        # see http://peewee.readthedocs.org/en/latest/peewee/database.html#error-2006-mysql-server-has-gone-away
        observium_db.connect()

        result = False

        try:
            result = self._get(request, format, **kwargs)
        finally:
            observium_db.close()

        return result

    def _get(self, request, format=None, **kwargs):
        if request.query_params.get('buildings', False):
            data = OrderedDict(copy.deepcopy(get_buildingmap_data().get('data')))
        else:
            data = OrderedDict(copy.deepcopy(CONFIG.get('WEATHERMAP_DATA').get('data')))

        all_ports = []
        for k, v in data.items():
            all_ports.extend(v['id'])

        ports = Ports.select(Ports).where(Ports.port << all_ports)

        for port in ports:
            for key, value in data.items():
                for portid in value['id']:
                    if port.port == portid:
                        value['A'] = value.get('A', 0) + port.ifoutoctets_rate * 8
                        value['Z'] = value.get('Z', 0) + port.ifinoctets_rate * 8
                        value['speed'] = value.get('speed', 0) + port.ifspeed if port.ifspeed else 0
                        value['timestamp'] = port.poll_time
                        value['poll_frequency'] = 300
                        value['isUp'] = bool(port.ifoperstatus == "up")

        for key, value in data.items():
            del value['id']

        data["timestamp"] = int(datetime.now().strftime('%s'))

        return Response(data, status=status.HTTP_200_OK)


class StatsAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None, **kwargs):
        app = request.GET.get('app')
        model = request.GET.get('model')
        column = request.GET.get('column')

        model_klass = apps.get_model(app_label=app, model_name=model)
        queryset = model_klass.objects.all()
        qs_stats = qsstats.QuerySetStats(queryset, column, aggregate=Count('pk'))

        xdata = ['Today', 'This Week', 'This Month']
        ydata = [qs_stats.this_day(), qs_stats.this_week(), qs_stats.this_month()]

        extra_serie1 = {"tooltip": {"y_start": "", "y_end": " %s" % model_klass._meta.verbose_name_plural.title()}}
        chartdata = {
            'x': xdata, 'name1': 'Hosts', 'y1': ydata, 'extra1': extra_serie1,
        }
        charttype = "discreteBarChart"
        chartcontainer = '%s_stats' % model.lower()
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

        return Response(context, template_name='api/web/ipam_stats.html')


class DashboardAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,)

    def get(self, request, format=None, **kwargs):
        wireless_networks = Network.objects.filter(dhcp_group__name__in=['aruba_wireless', 'aruba_wireless_eastern'])
        wireless_networks_available_qs = [Q(address__net_contained=network.network) for network in wireless_networks]
        wireless_addresses_total = Address.objects.filter(reduce(operator.or_, wireless_networks_available_qs)).count()
        wireless_addresses_avaiable = Address.objects.filter(reduce(operator.or_, wireless_networks_available_qs), leases__ends__lt=timezone.now()).count()
        wireless_addresses_inuse = wireless_addresses_total - wireless_addresses_avaiable

        data = (
            ('Static Hosts', '%s' % Host.objects.filter(addresses__isnull=False, expires__gte=timezone.now()).count(),),
            ('Dynamic Hosts', '%s' % Host.objects.filter(pools__isnull=False, expires__gte=timezone.now()).count(),),
            ('Active Leases', '%s' % Lease.objects.filter(ends__gte=timezone.now()).count(),),
            ('Abandoned Leases', '%s' % Lease.objects.filter(abandoned=True).count(),),
            ('Networks: (Total / Wireless)', '%s / %s' % (Network.objects.all().count(), wireless_networks.count()),),
            # ('Addresses: (Total / Available)', '%s / %s' % (
            #     Address.objects.all().count(),
            #     Address.objects.filter(host__isnull=True).count()),
            # ),
            ('Available Wireless Addresses', Address.objects.filter(reduce(operator.or_, wireless_networks_available_qs), leases__ends__lt=timezone.now()).count(),),
            ('DNS A Records', DnsRecord.objects.filter(dns_type__name__in=['A', 'AAAA']).count(),),
            ('DNS CNAME Records', DnsRecord.objects.filter(dns_type__name='CNAME').count(),),
            ('DNS MX Records', DnsRecord.objects.filter(dns_type__name='MX').count(),),
            ('Active Users Within 1 Year', User.objects.filter(last_login__gte=(timezone.now() - timedelta(days=365))).count(),),
        )

        data = OrderedDict(data)

        return Response(data, status=status.HTTP_200_OK)


class ServerHostCSVRenderer(CSVRenderer):
    header = ['hostname', 'mac', 'description', 'master_ip_address', 'user_owners', 'group_owners']


class ServerHostView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, ServerHostCSVRenderer,)

    def get(self, request, format=None, **kwargs):
        hosts = (
            Host.objects
            .prefetch_related('addresses')
            .filter(structured_attributes__structured_attribute_value__attribute__name='border-profile',
                    structured_attributes__structured_attribute_value__value='server')
        )

        user_perms_prefetch = UserObjectPermission.objects.select_related('permission', 'user').filter(
            content_type=ContentType.objects.get_for_model(Host),
            object_pk__in=[str(host.mac) for host in hosts],
            permission__codename='is_owner_host'
        )
        group_perms_prefetch = GroupObjectPermission.objects.select_related('permission', 'group').filter(
            content_type=ContentType.objects.get_for_model(Host),
            object_pk__in=[str(host.mac) for host in hosts],
            permission__codename='is_owner_host'
        )

        data = []
        for host in hosts:
            owners = host.get_owners(name_only=True, user_perms_prefetch=user_perms_prefetch, group_perms_prefetch=group_perms_prefetch)
            data.append({
                'hostname': host.hostname,
                'mac': str(host.mac),
                'description': host.description,
                'master_ip_address': host.ip_addresses[0] if host.ip_addresses else None,
                'user_owners': ', '.join(owners[0]),
                'group_owners': ', '.join(owners[1]),
            })

        if request.accepted_renderer.format == 'json':
            return Response({"data": data}, status=status.HTTP_200_OK)
        else:
            return Response(data, status=status.HTTP_200_OK)

@api_view(('GET',))
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def weathermap_config(request):
    data = copy.deepcopy(CONFIG.get('WEATHERMAP_DATA').get('config'))

    return Response(data)

@api_view(('GET',))
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def buildingmap_config(request):
    data = copy.deepcopy(get_buildingmap_data().get('config'))

    return Response(data)
