"""DNS API Views."""

from openipam.dns.models import DnsRecord, Domain, DnsType, DnsView, DhcpDnsRecord
from ..serializers.dns import (
    DNSSerializer,
    DomainSerializer,
    DNSCreateSerializer,
    DomainCreateSerializer,
)
from ..serializers.dns import (
    DnsTypeSerializer,
    DnsViewSerializer,
    DhcpDnsRecordSerializer,
)
from rest_framework import permissions
from .base import APIModelViewSet, APIPagination
from ..filters.dns import DnsFilter, DomainFilter
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.utils import DataError
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from guardian.shortcuts import get_objects_for_user


class DnsViewSet(APIModelViewSet):
    """API endpoint that allows dns records to be viewed or edited."""

    queryset = DnsRecord.objects.select_related("ip_content", "dns_type", "host").all()
    serializer_class = DNSSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_fields = ["name", "ip_content", "text_content", "dns_type"]
    filter_class = DnsFilter

    def delete(self, request, *args, **kwargs):
        """Delete a DNS record."""
        obj = self.get_object()
        LogEntry.objects.log_action(
            user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_text(obj),
            action_flag=DELETION,
            change_message="API Delete call.",
        )
        return super().delete(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a new DNS record."""
        try:
            print(f"\nrequest.aut: {request.auth}")
            serializer = DNSCreateSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=False)
            print(f"\nserializer.data: {serializer.data}")
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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


#  {
#             "name": "asdfaaa",
#             "text_content": "asdfasdf",
#             "dns_type": "TXT",
#             "ttl": 14400
# }


class DomainViewSet(APIModelViewSet):
    queryset = Domain.objects.select_related("changed_by").all()
    serializer_class = DomainSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_fields = ("name", "username")
    filter_class = DomainFilter

    def get_queryset(self):
        # If listing, filter on the user
        if self.action == "list":
            allowed_domains = get_objects_for_user(
                self.request.user,
                ["dns.add_records_to_domain", "dns.change_domain"],
                any_perm=True,
                use_groups=True,
                with_superuser=True,
            )
            return self.queryset.filter(pk__in=allowed_domains).select_related(
                "changed_by"
            )
        return self.queryset

    def create(self, request, *args, **kwargs):
        print(f"\nrequest.data: {request.data}")
        serializer = DomainCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        try:
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
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

    def partial_update(self, request, name=None):
        instance = Domain.objects.get(name=name)
        serializer = DomainSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, name=None):
        print(f"request params are {request.query_params}")
        domain = Domain.objects.get(name=name)
        limit = 25
        # Paginate this
        # dns_records = DnsRecord.objects.filter(name__endswith=domain.name)
        dns_records = DnsRecord.objects.filter(name__endswith=domain.name)
        page = request.query_params.get("page") or 1
        dns_records = dns_records[int(page) * limit : (int(page) + 1) * limit]
        dns_serializer = DNSSerializer(
            dns_records, many=True, context={"request": request}
        )
        serializer = DomainSerializer(domain)
        data = {"domain": serializer.data, "dns_records": dns_serializer.data}
        return Response(data)

    @action(detail=True, methods=["post"], serializer_class=DNSCreateSerializer)
    def add_dns_record(self, request, name=None):
        print(f"\n auth is {request.user}")
        request.data["name"] = request.data["name"] + "." + name
        serializer = DNSCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(f"serializer.data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Posting to domain/domainName should create a dns record.

    def partial_update(self, request, name=None):
        instance = Domain.objects.get(name=name)
        serializer = DomainSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, name=None):
        print(f"request params are {request.query_params}")
        domain = Domain.objects.get(name=name)
        limit = 25
        # Paginate this
        # dns_records = DnsRecord.objects.filter(name__endswith=domain.name)
        dns_records = DnsRecord.objects.filter(name__endswith=domain.name)
        page = request.query_params.get("page") or 1
        dns_records = dns_records[int(page) * limit : (int(page) + 1) * limit]
        dns_serializer = DNSSerializer(
            dns_records, many=True, context={"request": request}
        )
        serializer = DomainSerializer(domain)
        data = {"domain": serializer.data, "dns_records": dns_serializer.data}
        return Response(data)

    @action(detail=True, methods=["post"], serializer_class=DNSCreateSerializer)
    def add_dns_record(self, request, name=None):
        print(f"\n auth is {request.user}")
        request.data["name"] = request.data["name"] + "." + name
        serializer = DNSCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(f"serializer.data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Posting to domain/domainName should create a dns record.


class DnsTypeList(generics.ListAPIView):
    """API endpoint that allows dns types to be viewed."""

    permission_classes = [permissions.DjangoModelPermissions]
    pagination_class = APIPagination
    serializer_class = DnsTypeSerializer
    queryset = DnsType.objects.all()


class DnsViewsList(generics.ListAPIView):
    """API endpoint that allows dns types to be viewed."""

    permission_classes = [permissions.DjangoModelPermissions]
    pagination_class = APIPagination
    serializer_class = DnsViewSerializer
    queryset = DnsView.objects.all()


class DhcpDnsRecordsList(generics.ListAPIView):
    """API endpoint that allows dhcp dns records to be viewed."""

    permission_classes = [permissions.DjangoModelPermissions]
    pagination_class = APIPagination
    serializer_class = DhcpDnsRecordSerializer
    queryset = DhcpDnsRecord.objects.all()
