from django.db.models import Q

from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from openipam.network.models import Network, AddressType, NetworkRange


@api_view(('GET',))
@permission_classes((IsAuthenticated,))
@renderer_classes((TemplateHTMLRenderer,))
def network_selects(request, address_type_id):
    data = {}

    address_type = AddressType.objects.filter(id=address_type_id)
    if address_type:
        networks = Network.objects.by_address_type(address_type[0])
        data['networks'] = networks

    return Response(data, template_name='api/web/network_selects.html')
