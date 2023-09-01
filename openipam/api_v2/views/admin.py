from rest_framework.generics import ListAPIView
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

from ..filters.admin import LogEntryFilterSet
from ..filters.base import FieldChoiceFilter

from .base import LogsPagination
from ..serializers.admin import LogEntrySerializer, EmailLogSerializer
from openipam.log.models import EmailLog
from ..permissions import APIAdminPermission
from django_filters.rest_framework import DjangoFilterBackend


class LogEntryList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = LogEntry.objects.all().order_by("-action_time")

    serializer_class = LogEntrySerializer
    pagination_class = LogsPagination
    filter_backends = [FieldChoiceFilter, DjangoFilterBackend]
    filterset_class = LogEntryFilterSet
    filter_field = "content_type__model"
    filter_query_prefix = "include"
    filter_choices = [
        "host",
        "dnsrecord",
        "address",
        "user",
        "group",
        "domain",
    ]
    filter_allow_unlisted = True


class EmailLogsList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = EmailLog.objects.all().order_by("-when")
    serializer_class = EmailLogSerializer
    pagination_class = LogsPagination
