"""Miscellaneous views that don't really fit anywhere else."""

from rest_framework import viewsets as lib_viewsets
from .base import APIPagination
from ..serializers.misc import AttributeSerializer
from openipam.hosts.models import Attribute


class AttributeViewSet(lib_viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows attributes to be viewed or edited."""

    queryset = (
        Attribute.objects.select_related("changed_by").prefetch_related("choices").all()
    )
    serializer_class = AttributeSerializer
