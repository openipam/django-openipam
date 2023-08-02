"""DNS API Views."""

from django.shortcuts import get_object_or_404
from openipam.dns.models import DnsRecord, Domain, DnsType, DnsView, DhcpDnsRecord
from openipam.user.models import User
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
from ..filters.dns import DnsFilter
from ..filters.base import FieldSearchFilterBackend, RelatedPermissionFilter
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.utils import DataError
from guardian.shortcuts import get_objects_for_user, assign_perm, remove_perm
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.contrib.auth.models import Group


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
    queryset = Domain.objects.select_related("changed_by").order_by("-changed")
    serializer_class = DomainSerializer
    permission_classes = [permissions.DjangoObjectPermissions]
    filter_backends = [FieldSearchFilterBackend]

    search_fields = [("name", "name"), ("changed_by__username", "changed_by")]

    lookup_field = "name"
    lookup_value_regex = "(?:[a-z0-9\-]{1,63}\.){1,32}[a-z0-9\-]{2,63}"

    def get_queryset(self):
        # If listing, filter on the user
        if self.action == "list":
            allowed_domains = get_objects_for_user(
                self.request.user,
                [
                    "dns.add_records_to_domain",
                    "dns.is_owner_domain",
                    "dns.change_domain",
                ],
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
        domain = Domain.objects.get(name=name)
        # Paginate this
        # dns_records = DnsRecord.objects.filter(name__endswith=domain.name)
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], serializer_class=DNSSerializer)
    def records(self, request, name=None):
        domain = Domain.objects.get(name=name)
        dns_records = DnsRecord.objects.filter(name__endswith=domain.name)
        if not request.user.has_perm("is_owner_domain", domain):
            user_hosts = get_objects_for_user(
                request.user,
                ["hosts.is_owner_host", "hosts.change_host"],
                any_perm=True,
            )
            dns_records = dns_records.filter(host__in=user_hosts)
        # DNS record filtering
        dns_type = request.query_params.get("dns_type", None)
        if dns_type:
            dns_records = dns_records.filter(dns_type__name=dns_type)
        content = request.query_params.get("content", None)
        if content:
            dns_records = dns_records.filter(content__icontains=content)
        name = request.query_params.get("name", None)
        if name:
            dns_records = dns_records.filter(name__icontains=name)
        host = request.query_params.get("host", None)
        if host:
            dns_records = dns_records.filter(host__mac=host)
        pagination = APIPagination()
        page = pagination.paginate_queryset(dns_records, request)
        dns_serializer = DNSSerializer(page, many=True, context={"request": request})

        return pagination.get_paginated_response(dns_serializer.data)

    @records.mapping.post
    def add_dns_record(self, request, name=None):
        request.data["name"] = request.data["name"] + "." + name
        if not request.user.has_perm("dns.add_records_to_domain", name):
            return Response(
                {"detail": "You do not have permission to add records to this domain."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = DNSCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def users(self, request, name=None):
        domain = Domain.objects.get(name=name)
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("user_perms"))

    @users.mapping.post
    def add_user(self, request, name=None):
        domain = Domain.objects.get(name=name)
        user = get_object_or_404(User, username=request.data.get("user"))
        perm = request.data.get("perm")
        assign_perm(perm, user, domain)
        domain.save()
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("user_perms"))

    @users.mapping.delete
    def remove_user(self, request, name=None):
        domain = Domain.objects.get(name=name)
        user = get_object_or_404(User, username=request.data.get("user"))
        perm = request.data.get("perm")
        remove_perm(perm, user, domain)
        domain.save()
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("user_perms"))

    @action(detail=True, methods=["get"])
    def groups(self, request, name=None):
        domain = Domain.objects.get(name=name)
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("group_perms"))

    @groups.mapping.post
    def add_group(self, request, name=None):
        domain = Domain.objects.get(name=name)
        group = get_object_or_404(Group, name=request.data.get("group"))
        perm = request.data.get("perm")
        assign_perm(perm, group, domain)
        domain.save()
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("group_perms"))

    @groups.mapping.delete
    def remove_group(self, request, name=None):
        domain = Domain.objects.get(name=name)
        group = get_object_or_404(Group, name=request.data.get("group"))
        perm = request.data.get("perm")
        remove_perm(perm, group, domain)
        domain.save()
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("group_perms"))


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
    filter_backends = [RelatedPermissionFilter]
    filter_related_field = "host"
    filter_perms = ["hosts.is_owner_host", "hosts.change_host"]
    filter_staff_sees_all = True
    queryset = DhcpDnsRecord.objects.all()
