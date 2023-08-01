from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.contrib.admin.models import LogEntry
from ..filters.base import FieldChoiceFilter

from .base import LogsPagination
from ..serializers.admin import LogEntrySerializer, EmailLogSerializer
from openipam.log.models import EmailLog
from ..permissions import APIAdminPermission


class LogEntryList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = LogEntry.objects.all().order_by("-action_time")
    serializer_class = LogEntrySerializer
    pagination_class = LogsPagination
    filter_backends = [FieldChoiceFilter]
    filter_field = "content_type__model"
    filter_query_prefix = "include"
    filter_choices = [
        "host",
        "dnsrecord",
        "address",
        "user",
    ]


class HostLogsList(APIView):
    def get(self, request, format=None):
        # redirect
        return Response(
            status=301, headers={"Location": "/api/v2/admin/logs/?include_host=1"}
        )


class EmailLogsList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = EmailLog.objects.all().order_by("-when")
    serializer_class = EmailLogSerializer
    pagination_class = LogsPagination


class DnsLogsList(APIView):
    def get(self, request, format=None):
        # redirect
        return Response(
            status=301, headers={"Location": "/api/v2/admin/logs/?include_dnsrecord=1"}
        )


class AddressLogsList(APIView):
    def get(self, request, format=None):
        # redirect
        return Response(
            status=301, headers={"Location": "/api/v2/admin/logs/?include_address=1"}
        )


class UserLogsList(APIView):
    def get(self, request, format=None):
        return Response(
            status=301, headers={"Location": "/api/v2/admin/logs/?include_user=1"}
        )
