from rest_framework.generics import ListAPIView
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from ..filters.base import FieldChoiceFilter

from .base import LogsPagination
from ..serializers.admin import LogEntrySerializer, EmailLogSerializer
from openipam.log.models import EmailLog
from ..permissions import APIAdminPermission


class LogEntryList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = LogEntry.objects.all().order_by("-action_time")

    def get_queryset(self):
        queryset = super().get_queryset()
        type = self.request.query_params.get("type", None)
        flag = self.request.query_params.get("action_flag", None)
        user = self.request.query_params.get("user", None)
        if type:
            queryset = queryset.filter(content_type__model=type)
        if flag:
            if flag == "Addition":
                flag = ADDITION
            elif flag == "Change":
                flag = CHANGE
            elif flag == "Deletion":
                flag = DELETION
            queryset = queryset.filter(action_flag=flag)
        if user:
            queryset = queryset.filter(user__username=user)
        return queryset

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
        "group",
        "domain",
    ]
    filter_allow_unlisted = True


class EmailLogsList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = EmailLog.objects.all().order_by("-when")
    serializer_class = EmailLogSerializer
    pagination_class = LogsPagination
