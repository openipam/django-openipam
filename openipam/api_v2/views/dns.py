"""DNS API Views."""

from rest_framework import permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from guardian.shortcuts import get_objects_for_user, assign_perm, remove_perm
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.contrib.auth.models import Group
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from openipam.dns.models import DnsRecord, Domain, DnsType, DnsView, DhcpDnsRecord
from openipam.user.models import User
from .base import APIModelViewSet, APIPagination
from ..filters.dns import DhcpDnsFilter, DnsFilter, DomainFilter
from ..filters.base import RelatedPermissionFilter
from ..permissions import DnsRecordPermissions
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


class DnsViewSet(APIModelViewSet):
    """API endpoint that allows dns records to be viewed or edited."""

    queryset = DnsRecord.objects.select_related("ip_content", "dns_type", "host").all()
    serializer_class = DNSSerializer
    permission_classes = [DnsRecordPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DnsFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        host = self.request.query_params.get("host", None)
        mac = self.request.query_params.get("mac", None)
        if host:
            queryset = queryset.filter(host__hostname=host)
        if mac:
            queryset = queryset.filter(host__mac=mac)
        return queryset

    def get_serializer_class(self):
        """Return the serializer class."""
        # Necessary to use a different serializer for create
        if self.action == "create":
            return DNSCreateSerializer
        return self.serializer_class

    def perform_destroy(self, instance):
        """Implement logging for deletion."""
        LogEntry.objects.log_action(
            user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(instance).pk,
            object_id=instance.pk,
            object_repr=force_text(instance),
            action_flag=DELETION,
            change_message=f"Deleting DNS record",
        )
        super().perform_destroy(instance)

    def create(self, request, *args, **kwargs):
        """Create a DNS record."""
        # check permissions on domain. Can't rely on the permission class
        # because we don't have the domain name yet.
        domain_name = ".".join(request.data.get("name").split(".")[1:])
        domain = get_object_or_404(Domain, name=domain_name)

        if not request.user.has_perm(
            "dns.add_records_to_domain", domain
        ) and not request.user.has_perm("dns.is_owner_domain", domain):
            return Response(
                {"detail": "You do not have permission to add records to this domain."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # We have permission, so create the record
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], queryset=DnsType.objects.all())
    def types(self, request: Request, *args, **kwargs):
        """Return a list of DNS types."""
        types = self.get_queryset()
        serializer = DnsTypeSerializer(types, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], queryset=DnsView.objects.all())
    def views(self, request: Request, *args, **kwargs):
        """Return a list of DNS views."""
        views = self.get_queryset()
        serializer = DnsViewSerializer(views, many=True)
        return Response(serializer.data)

    filter_related_field = "host"
    filter_perms = ["hosts.is_owner_host", "hosts.change_host"]
    filter_staff_sees_all = True

    @action(
        detail=False,
        methods=["get"],
        queryset=DhcpDnsRecord.objects.select_related("domain", "host").all(),
        filter_backends=[RelatedPermissionFilter],
        serializer_class=DhcpDnsRecordSerializer,
    )
    def dhcp(self, request: Request, *args, **kwargs):
        """Return a list of DHCP DNS records."""
        records = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(records)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class DomainViewSet(APIModelViewSet):
    """API endpoint that allows domains to be viewed or edited."""

    queryset = (
        Domain.objects.select_related("changed_by")
        .annotate(record_count=Count("dnsrecord"))
        .order_by("-record_count")
    )
    serializer_class = DomainSerializer
    permission_classes = [permissions.DjangoObjectPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DomainFilter

    lookup_field = "name"
    lookup_value_regex = r"(?:[a-z0-9\-]{1,63}\.){1,32}[a-z0-9\-]{2,63}"

    def get_serializer_class(self):
        """Return the serializer class."""
        # Necessary to use a different serializer for create
        if self.action == "create":
            return DomainCreateSerializer
        return self.serializer_class

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

    def update(self, *args, **kwargs):
        """Updates to domains are not permitted, as DNS records would not be updated."""
        return Response(
            {"detail": "Cannot update a domain. Create a new one."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, *args, **kwargs):
        """Updates to domains are not permitted, as DNS records would not be updated."""
        return Response(
            {"detail": "Cannot update a domain. Create a new one."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def retrieve(self, request, *args, name=None, **kwargs):
        domain = Domain.objects.get(name=name)
        serializer = DomainSerializer(domain, context={"request": request})
        data = serializer.data.copy()
        return Response(data)

    filter_related_field = "host"
    filter_perms = ["hosts.is_owner_host", "hosts.change_host"]
    filter_staff_sees_all = True

    @action(
        detail=True,
        methods=["get"],
        serializer_class=DhcpDnsRecordSerializer,
        queryset=DhcpDnsRecord.objects.select_related("domain", "host").all(),
        filter_backends=[DjangoFilterBackend, RelatedPermissionFilter],
        filterset_class=DhcpDnsFilter,
        url_path="dhcp",
    )
    def dhcp_records(self, request, name=None):
        """Get DHCP DNS records for a domain."""
        domain = Domain.objects.get(name=name)
        # Pull the records for this domain
        dhcp_records = self.filter_queryset(self.get_queryset().filter(domain=domain))
        # If the user doesn't own the domain, filter the records to only show
        # records for hosts they own.
        if not request.user.has_perm(
            "dns.add_records_to_domain", domain
        ) and not request.user.has_perm("dns.is_owner_domain", domain):
            user_hosts = get_objects_for_user(
                request.user,
                [
                    "hosts.is_owner_host",
                    "hosts.change_host",
                ],
                any_perm=True,
                use_groups=True,
                with_superuser=False,
            )
            dhcp_records = dhcp_records.filter(host__in=user_hosts)
        # Serialize the records
        pagination = self.paginate_queryset(dhcp_records)
        serializer = self.get_serializer(pagination, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        serializer_class=DNSSerializer,
        permission_classes=[permissions.IsAuthenticated],
        filter_backends=[DjangoFilterBackend],
        filterset_class=DnsFilter,
        queryset=DnsRecord.objects.select_related("ip_content", "dns_type", "host"),
    )
    def records(self, request, name=None):
        """Get DNS records for a domain."""
        domain = Domain.objects.get(name=name)
        # Pull the records for this domain
        dns_records = self.filter_queryset(self.get_queryset().filter(domain=domain))
        # If the user doesn't own the domain, filter the records to only show
        # records for hosts they own.
        # This is not a security measure, but rather something to make the UI
        # more usable. Generally, if a user merely has "add_records_to_domain"
        # permission, they don't have permission to delete other users' records,
        # and probably only want to see their own records.
        # The only way to determine ownership of DNS records at the moment is
        # to check if the user has permission to change the host. Record-level
        # permissions are not implemented.
        if not request.user.has_perm("is_owner_domain", domain):
            user_hosts = get_objects_for_user(
                request.user,
                ["hosts.is_owner_host", "hosts.change_host"],
                any_perm=True,
            )
            dns_records = dns_records.filter(host__in=user_hosts)
        pagination = APIPagination()
        page = pagination.paginate_queryset(dns_records, request)
        dns_serializer = DNSSerializer(page, many=True, context={"request": request})

        return pagination.get_paginated_response(dns_serializer.data)

    @records.mapping.post
    def add_dns_record(self, request: Request, name=None):
        """Add a DNS record to a domain.

        Takes the same data as POSTing to the /dns/ endpoint, but appends the domain name.
        """
        data = request.data.copy()
        data["name"] = request.data["name"] + "." + name
        domain = get_object_or_404(Domain, name=name)
        # check permissions on domain. Can't rely on the permission class, since
        # we're not modifying the domain itself.
        if not request.user.has_perm(
            "dns.add_records_to_domain", domain
        ) and not request.user.has_perm("dns.is_owner_domain", domain):
            return Response(
                {"detail": "You do not have permission to add records to this domain."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # We have permission, so create the record
        serializer = DNSCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        # Log the action
        LogEntry.objects.log_action(
            user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=f"{obj.name} {obj.dns_type.name} {obj.content}",
            action_flag=1,
            change_message="API Create call.",
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def users(self, request, name=None):
        """Get users with permissions on a domain."""
        domain = Domain.objects.get(name=name)
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("user_perms"))

    @users.mapping.post
    def add_user(self, request, name=None):
        """Add a user to a domain."""
        domain = Domain.objects.get(name=name)
        # Only admins can add users to domains
        if not request.user.is_ipamadmin:
            return Response(
                {"detail": "You do not have permission to add users to this domain."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(User, username=request.data.get("user"))
        perm = request.data.get("perm")
        assign_perm(perm, user, domain)
        domain.save()
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("user_perms"))

    @users.mapping.delete
    def remove_user(self, request, name=None):
        """Remove a user from a domain."""
        domain = Domain.objects.get(name=name)
        # Only admins can remove users from domains
        if not request.user.is_ipamadmin:
            return Response(
                {
                    "detail": "You do not have permission to remove users from this domain."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(User, username=request.data.get("user"))
        perm = request.data.get("perm")
        remove_perm(perm, user, domain)
        domain.save()
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("user_perms"))

    @action(detail=True, methods=["get"])
    def groups(self, request, name=None):
        """Get groups with permissions on a domain."""
        domain = Domain.objects.get(name=name)
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("group_perms"))

    @groups.mapping.post
    def add_group(self, request, name=None):
        """Add a group to a domain."""
        domain = Domain.objects.get(name=name)
        # Only admins can add groups to domains
        if not request.user.is_ipamadmin:
            return Response(
                {"detail": "You do not have permission to add groups to this domain."},
                status=status.HTTP_403_FORBIDDEN,
            )
        group = get_object_or_404(Group, name=request.data.get("group"))
        perm = request.data.get("perm")
        assign_perm(perm, group, domain)
        domain.save()
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("group_perms"))

    @groups.mapping.delete
    def remove_group(self, request, name=None):
        """Remove a group from a domain."""
        domain = Domain.objects.get(name=name)
        # Only admins can remove groups from domains
        if not request.user.is_ipamadmin:
            return Response(
                {
                    "detail": "You do not have permission to remove groups from this domain."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        group = get_object_or_404(Group, name=request.data.get("group"))
        perm = request.data.get("perm")
        remove_perm(perm, group, domain)
        domain.save()
        serializer = DomainSerializer(domain, context={"request": request})
        return Response(serializer.data.get("group_perms"))


class DnsTypeList(generics.ListAPIView):
    """API endpoint that allows dns types to be viewed."""

    permission_classes = [permissions.DjangoModelPermissions]
    pagination_class = APIPagination
    serializer_class = DnsTypeSerializer
    queryset = DnsType.objects.all()


class DnsViewsList(generics.ListAPIView):
    """API endpoint that allows dns views to be viewed."""

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
    queryset = DhcpDnsRecord.objects.select_related("domain", "host").all()

    def get_queryset(self):
        queryset = super().get_queryset()
        domain = self.request.query_params.get("domain", None)
        ip_content = self.request.query_params.get("ip_content", None)
        host = self.request.query_params.get("host", None)
        mac = self.request.query_params.get("mac", None)
        if host:
            queryset = queryset.filter(host__hostname=host)
        if mac:
            queryset = queryset.filter(host__mac=mac)
        if domain:
            queryset = queryset.filter(domain__name__endswith=domain)
        if ip_content:
            queryset = queryset.filter(ip_content__ip_lower=ip_content)
        return queryset
