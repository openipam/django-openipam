from django.db.models import Q

from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes

from openipam.network.models import Network, AddressType, NetworkRange


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def network_selects(request, address_type_id):

    address_type = AddressType.objects.get(id=address_type_id)
    networks = Network.objects.get_networks_from_address_type(address_type)

    data = {
        'networks': networks
    }

    return Response(data, template_name='api/web/network_selects.html')
