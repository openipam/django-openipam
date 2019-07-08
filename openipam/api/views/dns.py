from django.db import DataError
from django.core.exceptions import ValidationError
from django.contrib.admin.models import DELETION, LogEntry
from django.utils.encoding import force_text
from django.contrib.contenttypes.models import ContentType

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from openipam.dns.models import Domain, DnsRecord
from openipam.api.views.base import APIPagination
from openipam.api.filters.dns import DomainFilter, DnsFilter
from openipam.api.serializers.dns import (
    DomainNameSerializer,
    DomainSerializer,
    DnsListDetailSerializer,
    DnsCreateSerializer,
    DnsDeleteSerializer,
)


class DomainNameList(generics.ListAPIView):
    queryset = Domain.objects.select_related().all()
    permission_classes = (AllowAny,)
    serializer_class = DomainNameSerializer
    fields = ("name",)
    filter_fields = ("name", "username")
    filter_class = DomainFilter
    pagination_class = APIPagination


class DomainList(generics.ListAPIView):
    queryset = Domain.objects.select_related().all()
    serializer_class = DomainSerializer
    filter_fields = ("name", "username")
    filter_class = DomainFilter
    pagination_class = APIPagination


class DnsList(generics.ListAPIView):
    queryset = DnsRecord.objects.select_related("ip_content", "dns_type", "host").all()
    serializer_class = DnsListDetailSerializer
    filter_fields = ("name", "ip_content", "text_content", "dns_type")
    filter_class = DnsFilter
    pagination_class = APIPagination


class DnsDetail(generics.RetrieveAPIView):
    """
        Gets details for a Dns Record.
    """

    queryset = DnsRecord.objects.select_related("ip_content", "dns_type", "host").all()
    serializer_class = DnsListDetailSerializer


class DnsCreate(generics.CreateAPIView):
    """
        Create a Dns Record.

        **Required Arguments**:

        * `name` -- Dns Record name.
        * `type` -- Dns Record type.
        * `content` --  Dns Record content.

        **Optional Arguments**:

        * `ttl` -- Time to live. Defaults to 14400.

        **Example**:

            {
                "name": "test.me.com",
                "type": "CNAME",
                "content": "test.com",
                "ttl": "14440"
            }
    """

    serializer_class = DnsCreateSerializer
    model = DnsRecord

    def create(self, request, *args, **kwargs):
        try:
            response = super(DnsCreate, self).create(request, *args, **kwargs)
            return response
        except (ValidationError, DataError) as e:
            error_list = []
            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append("%s: %s" % (key.capitalize(), error))
            else:
                error_list.append(e.message)
            return Response(
                {"non_field_errors": error_list}, status=status.HTTP_400_BAD_REQUEST
            )


class DnsDelete(generics.DestroyAPIView):
    """
        Delete a Dns Record.

        All that is required for this to execute is calling it via a POST or DELETE request.
    """

    serializer_class = DnsDeleteSerializer
    queryset = DnsRecord.objects.all()

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post_delete(self, obj):
        """
        Placeholder method for calling after deleting an object.
        """
        LogEntry.objects.log_action(
            user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_text(obj),
            action_flag=DELETION,
            change_message="API Delete call.",
        )
