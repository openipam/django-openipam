from django.db.models import Q
from django.contrib.auth import get_user_model

from rest_framework.renderers import (
    TemplateHTMLRenderer,
    JSONRenderer,
    BrowsableAPIRenderer,
)
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from openipam.network.models import Network, AddressType, NetworkRange
from openipam.hosts.models import StructuredAttributeValue

from guardian.shortcuts import get_objects_for_user

User = get_user_model()


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
@renderer_classes((TemplateHTMLRenderer,))
def network_selects(request, address_type_id, use_permissions=True):
    data = {}

    address_type = AddressType.objects.filter(id=address_type_id)
    if address_type:
        networks = Network.objects.by_address_type(address_type[0])
        if use_permissions:
            # Networks user has permission to.
            user_nets = get_objects_for_user(
                request.user,
                [
                    "network.add_records_to_network",
                    "network.is_owner_network",
                    "network.change_network",
                ],
                any_perm=True,
            )
            networks = networks.filter(network__in=user_nets)
        data["networks"] = networks

    return Response(data, template_name="api/web/network_selects.html")


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
@renderer_classes((TemplateHTMLRenderer,))
def structured_attribute_selects(request, attribute_id, use_permissions=True):
    data = {}

    structured_attribute_values = StructuredAttributeValue.objects.filter(
        attribute__pk=attribute_id
    )
    data["structured_attribute_values"] = structured_attribute_values

    return Response(data, template_name="api/web/structured_attribute_selects.html")


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
@renderer_classes((TemplateHTMLRenderer,))
def show_users(request, group_id, use_permissions=True):
    data = {}

    users_from_group = User.objects.filter(groups__id=group_id)
    data["users_from_group"] = users_from_group

    return Response(data, template_name="api/web/show_users.html")
