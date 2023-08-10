from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions as base_permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers.network import NetworkSerializer
from .base import APIPagination
from openipam.network.models import Address, Network
from netfields import NetManager  # noqa


class NetworkViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows networks to be viewed"""

    # TODO: figure out how to support editing networks. This is a read-only viewset
    # for now.

    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    # TODO: Add filterset class

    @action(detail=True, methods=["get"])
    def addresses(self, request, pk=None):
        """Return all addresses in a given network."""
        network = self.get_object()
        addresses = Address.objects.filter(network=network)
        serializer = NetworkSerializer(addresses, many=True)
        return Response(serializer.data)
