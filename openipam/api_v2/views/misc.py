"""Miscellaneous views that don't really fit anywhere else."""

from rest_framework import viewsets as lib_viewsets
from ..serializers.misc import AttributeSerializer
from openipam.hosts.models import Attribute, StructuredAttributeValue
from django.db.models import Prefetch


class AttributeViewSet(lib_viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows attributes to be viewed or edited."""

    queryset = (
        Attribute.objects.select_related("changed_by")
        .prefetch_related(
            Prefetch(
                "choices",
                queryset=StructuredAttributeValue.objects.select_related("changed_by"),
            )
        )
        .all()
    )
    serializer_class = AttributeSerializer
