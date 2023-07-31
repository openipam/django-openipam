"""DNS API Views."""

from openipam.dns.models import DnsRecord, Domain, DnsType, DnsView, DhcpDnsRecord
from ..serializers.dns import DNSSerializer, DomainSerializer, DNSCreateSerializer, DomainCreateSerializer
from ..serializers.dns import DnsTypeSerializer, DnsViewSerializer, DhcpDnsRecordSerializer
from rest_framework import permissions
from .base import APIModelViewSet, APIPagination
from ..filters.dns import DnsFilter, DomainFilter
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.utils import DataError
from guardian.shortcuts import get_objects_for_user

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class DnsViewSet(APIModelViewSet):
    """API endpoint that allows dns records to be viewed or edited."""

    queryset = DnsRecord.objects.select_related("ip_content", "dns_type", "host").all()
    serializer_class = DNSSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterFields = ["name", "ip_content", "text_content", "dns_type"]
    filterClass = DnsFilter

    def create(self, request, *args, **kwargs):
        """Create a new DNS record."""
        try:
            serializer = DNSCreateSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=False)
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


class DomainViewSet(APIModelViewSet):
    queryset = Domain.objects.select_related('changed_by').all()
    serializer_class = DomainSerializer
    permission_classes = [permissions.IsAdminUser]
    filterFields = ("name", "username")
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
            return self.queryset.filter(pk__in=allowed_domains).select_related('changed_by')
        return self.queryset

    def create(self, request, *args, **kwargs):
        serializer = DomainCreateSerializer(data=request.data, context={"request": request})
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


class DnsTypeList(generics.ListAPIView):
    """API endpoint that allows dns types to be viewed."""
    permission_classes = [permissions.IsAdminUser]
    pagination_class = APIPagination
    serializer_class = DnsTypeSerializer
    queryset = DnsType.objects.all()


class DnsViewsList(generics.ListAPIView):
    """API endpoint that allows dns types to be viewed."""
    permission_classes = [permissions.IsAdminUser]
    pagination_class = APIPagination
    serializer_class = DnsViewSerializer
    queryset = DnsView.objects.all()


class DhcpDnsRecordsList(generics.ListAPIView):
    """API endpoint that allows dhcp dns records to be viewed."""
    permission_classes = [permissions.IsAdminUser]
    pagination_class = APIPagination
    serializer_class = DhcpDnsRecordSerializer
    queryset = DhcpDnsRecord.objects.all()
