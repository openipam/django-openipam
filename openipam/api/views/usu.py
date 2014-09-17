from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.views.decorators.cache import cache_page

from openipam.usu.models import Ports, Portsstate
from openipam.network.models import Network

from netaddr import IPNetwork

import requests

import itertools

from datetime import datetime

from collections import OrderedDict


@api_view(('GET',))
@permission_classes((IsAuthenticated,))
#@cache_page(60)
def subnet_data(request):
    network_blocks = request.REQUEST.get('network_blocks')
    network_tags = request.REQUEST.get('network_tags')
    by_router = request.REQUEST.get('by_router')

    if network_blocks:
        show_blocks = '&'.join(['show_blocks=%s' % n for n in network_blocks.split(',')])
        url = 'https://gul.usu.edu/subnetparser.py?format=json&%s' % show_blocks
        lease_data = requests.get(url, auth=('django-openipam', 'ZEraWDJ1aSLsYmzvqhUT2ZL4z2xpA9Yt')).json()
    elif network_tags:
        network_tags = network_tags.split(',')
        networks = Network.objects.filter(dhcp_group__name__in=network_tags)
        show_blocks = '&'.join(['show_blocks=%s' % str(n.network) for n in networks])
        url = 'https://gul.usu.edu/subnetparser.py?format=json&%s' % show_blocks
        lease_data = requests.get(url, auth=('django-openipam', 'ZEraWDJ1aSLsYmzvqhUT2ZL4z2xpA9Yt')).json()
    else:
        lease_data = requests.get('https://gul.usu.edu/subnetparser.py?format=json',
            auth=('django-openipam', 'ZEraWDJ1aSLsYmzvqhUT2ZL4z2xpA9Yt')).json()
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
        if ratio < 0: ratio = 0
        if ratio > 1: ratio = 1

        r = ratio * 2.0 - 1
        g = ratio * 2.0

        if r < 0.0: r = 0.0
        if g > 1.0: g = 1.0

        rgb = ((1-r) * 255, g * 255, 0)
        color = "#%02x%02x%02x" % rgb
        return color

    if not by_router:
        for item in lease_data:
            child = item

            if 'usage' in item:
                child['ratio'] = get_ratio(item['usage']['available'], item['usage']['dynamic'])
            else:
                child['ratio'] = 1

            if 'ratio' in item:
                child['style'] = color(child['ratio'])
            else:
                child['style'] = '#77f'

        return Response(lease_data, status=status.HTTP_200_OK)

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
        #{'router': '.gw.usu.edu', 'color': '#9f9', },
        {'router': 'aste.gw.usu.edu', 'color': '#f99', },
        {'router': 'brigham.gw.usu.edu', 'color': '#9f9', },
        {'router': 'ceu.gw.usu.edu', 'color': '#99f', },
        {'router': 'blanding.gw.usu.edu', 'color': '#66d', },
        {'router': 'UEN', 'color': '#f64', },
        {'router': 'multiple', 'color': '#999', },
    ]




    for key, group in itertools.groupby(lease_data, lambda item: item['router']):
        router = {
            'name': key if key is not None else 'FREE',
            'children': [],
        }

        if key is not None:
            _color = filter(lambda x: x['router'] == key, routers_css)
            if _color:
                router['style'] = _color[0]['color']
        else:
            router['style'] = '#00ff00'


        second_child = {
            'name': 'smaller',
            'children': [],
            'style': '#77f',
            'ratio': 1
        }
        third_child = {
            'name': 'smaller',
            'children': [],
            'style': '#77f',
            'ratio': 1
        }
        for item in group:
            network = IPNetwork(item['network'])
            child = item

            #else:
            #    child['style'] = '#00ff00'

            if 'usage' in item:
                child['ratio'] = get_ratio(item['usage']['available'], item['usage']['dynamic'])
            else:
                child['ratio'] = 1

            #if key is not None:
            if 'ratio' in item:
                child['style'] = color(child['ratio'])
            else:
                child['style'] = '#77f'

            child['name'] = item['network']
            child['size'] = network.prefixlen
            child['value'] = network.prefixlen
            del child['router']

            if network.prefixlen > 28:
                third_child['children'].append(child)
            elif network.prefixlen > 24:
                second_child['children'].append(child)
            else:
                router['children'].append(child)

        if third_child['children']:
            ratio_min = min([child['ratio'] for child in third_child['children'] if child['ratio'] is not None])
            third_child['style'] = color(ratio_min)
            second_child['children'].append(third_child)

        if second_child['children']:
            ratio_min = min([child['ratio'] for child in second_child['children'] if child['ratio'] is not None])
            # if router['name'] == 'FREE':
            #     for child in second_child['children']:
            #         if child['ratio'] < 1:
            #             print child
            second_child['style'] = color(ratio_min)

            router['children'].append(second_child)

        grouped_lease_data['children'].append(router)

    return Response(grouped_lease_data, status=status.HTTP_200_OK)


@api_view(('GET',))
@permission_classes((AllowAny,))
def weather_data(request):

    data = OrderedDict({
        "MAIN-RPARK": {'id': [19299]},
        "MAIN-ED": {'id': [19298]},
        "MAIN-SER": {'id': [19300]},
        "RPARK-ASTE": {'id': [19977]},
        "RPARK-SER": {'id': [19975]},
        "RPARK-SPEC": {'id': [19972]},
        "SER-ED": {'id': [2502]},
        "SER-SPEC": {'id': [2500]},
        "SER-ASTE": {'id': [2503]},
        "SER-HOUS": {'id': [2506]},
        "SER-BR": {'id': [2509]},
        "BR-UEN-A": {'id': [19202]},
        "BR-UEN-B": {'id': [19200]},
        "SER-BR-BYP": {'id': [156616]},
        "SER-BR-SEC": {'id': [2510]},
        "CORE-SER": {'id': [3129, 3125]},
        "CORE-NEWSER": {'id': [3052, 3096, 3049, 3093]},
        "CORE-DMZ": {'id': [3046, 3086, 3045, 3088]},
    })

    all_ports = []
    for k, v in data.items():
        all_ports.extend(v['id'])

    ports = (
        Ports.select(Ports, Portsstate)
            .join(Portsstate, on=(Portsstate.port == Ports.port).alias('portstate'))
            .where(Ports.port << all_ports)
    )

    for port in ports:
        for key, value in data.items():
            for portid in value['id']:
                if port.port == portid:
                    value['A'] = value.get('A', 0) + port.portstate.ifoutoctets_rate * 8
                    value['Z'] = value.get('Z', 0) + port.portstate.ifinoctets_rate * 8
                    value['speed'] = value.get('speed', 0) + port.ifspeed
                    value['timestamp'] = port.portstate.poll_time
                    value['poll_frequency'] = 300

    for key, value in data.items():
        del value['id']

    data["timestamp"] =  int(datetime.now().strftime('%s'))

    return Response(data, status=status.HTTP_200_OK)


