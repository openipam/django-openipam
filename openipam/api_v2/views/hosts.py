"""Host API Views."""

from openipam.hosts.models import Host
from ..serializers.hosts import HostSerializer
from rest_framework import permissions
from .base import APIModelViewSet


class HostViewSet(APIModelViewSet):
    """API endpoint that allows hosts to be viewed or edited."""

    queryset = Host.objects.prefetch_related("addresses", "leases", "pools").all()
    serializer_class = HostSerializer
    permission_classes = [permissions.IsAuthenticated]
