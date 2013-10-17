from django.db.models import Q

from rest_framework.generics import ListAPIView
from rest_framework.filters import DjangoFilterBackend
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes

from openipam.network.models import Network, AddressType, NetworkRange
from openipam.api.serializers.network import NetworkSerializer
from openipam.api.filters.network import NetworkFilter

import operator


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def network_selects(request, address_id):

    assigned_ranges = NetworkRange.objects.filter(address_ranges__isnull=False)

    address_type = AddressType.objects.get(id=address_id)
    net_range = address_type.ranges.all()
    if net_range:
        q_list = [Q(network__net_contained_or_equal=net.range) for net in net_range]
        networks = Network.objects.filter(reduce(operator.or_, q_list))
    elif address_type.is_default:
        q_list = [Q(network__net_contained_or_equal=net.range) for net in assigned_ranges]
        networks = Network.objects.exclude(reduce(operator.or_, q_list))
    else:
        networks = None

    data = {
        'networks': networks
    }
    return Response(data, template_name='api/web/network_selects.html')
