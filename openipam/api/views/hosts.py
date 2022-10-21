from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import DataError

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer

from rest_framework_csv.renderers import CSVRenderer
from openipam.dns.models import DnsType
from openipam.hosts.actions import populate_primary_dns

from openipam.hosts.models import (
    Host,
    StructuredAttributeToHost,
    FreeformAttributeToHost,
    Attribute,
    StructuredAttributeValue,
    Disabled,
)
from openipam.network.models import Lease
from openipam.api.views.base import APIPagination, APIMaxPagination
from openipam.api.serializers import hosts as host_serializers
from openipam.api.filters.hosts import HostFilter
from openipam.api.permissions import IPAMChangeHostPermission, IPAMAPIAdminPermission

from guardian.shortcuts import assign_perm, remove_perm

from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()


class HostCSVRenderer(CSVRenderer):
    header = ["hostname", "mac", "master_ip_address", "expires"]

    def render(self, data, media_type=None, renderer_context={}, writer_opts=None):
        data = data["results"]
        return super(HostCSVRenderer, self).render(
            data, media_type, renderer_context, writer_opts
        )


class HostList(generics.ListAPIView):
    """
    Lists hosts based on given criteria.

    **Optional Filters**

    * `mac` -- MAC Address contains
    * `hostname` -- Hostname contains
    * `hostname_exact` -- Hostname exact
    * `user` -- Username of a user
    * `user_with_groups` -- Username of a user.  This will display the users hosts as well as all hosts in the users groups.
    * `group` -- Group name of a group.  To speficy multiple groups as a union, user a | between group names.
    * `is_expired` -- 1 or 0 to see expired hosts
    * `ip_address` -- IP Address to filter on
    * `attributes` -- 1 or 0 to show attributes on a host.
    * `attribute` -- Name:Value to filter on attributes
    * `limit` -- Number to enforce limit of records, default is 50, 0 shows all records (up to max of 5000).
    * `datetime` -- Date/Time of registered device.

    **Example**:

        /api/hosts/?group=switches&limit=0
    """

    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, HostCSVRenderer)
    queryset = Host.objects.prefetch_related("addresses", "leases", "pools").all()
    serializer_class = host_serializers.HostListSerializer
    pagination_class = APIMaxPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = HostFilter
    ordering_fields = ("expires", "changed")
    ordering = ("expires",)

    # def get_paginate_by(self, queryset=None):
    #     param = self.request.QUERY_PARAMS.get(self.paginate_by_param)
    #     if param and param == '0':
    #         return self.max_paginate_by
    #     else:
    #         return super(HostList, self).get_paginate_by()


class HostMac(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        ip_address = request.GET.get("ip_address")
        leased_ip = request.GET.get("leased_ip")
        registered_ip = request.GET.get("registered_ip")
        host = None

        if ip_address:
            host = Host.objects.filter(
                Q(leases__address__address=ip_address)
                | Q(addresses__address=ip_address)
            ).first()

        elif leased_ip:
            lease = Lease.objects.filter(address=leased_ip).first()
            if lease:
                return Response({"mac": str(lease.host_id)})

        elif registered_ip:
            host = Host.objects.filter(addresses__address=registered_ip).first()

        if host:
            return Response({"mac": str(host.mac)})

        return Response({})


class HostNextMac(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        vendor = request.GET.get("vendor")

        if vendor:
            next_mac = Host.objects.find_next_mac(vendor)
            return Response(next_mac)

        return Response("")


class HostDetail(generics.RetrieveAPIView):
    """
    Gets details for a host.
    """

    queryset = Host.objects.prefetch_related("addresses", "leases").all()
    permission_classes = (IsAuthenticated,)
    serializer_class = host_serializers.HostDetailSerializer


class HostCreate(generics.CreateAPIView):
    """
    Registers a new host.

    **Required Arguments**:

    * `mac` -- A MAC Address for the host.
    * `hostname` -- A unique hostname.
    * `pool`, `network`, or `ip_address` --  A pool name, network CIDR address, or ip address.
    * `expire_days` -- Number of days until expiration.  Choices currently are:  1, 7, 14, 30, 180, 365

    **Optional Arguments**:

    * `description` -- A text description of the host.
    * `dhcp_group` -- A DHCP Group id for this host.  Administrators Only.

    **Example**:

        {
            "mac": "00:00:00:00:00:00",
            "hostname": "hostname.usu.edu",
            "ip_address": "129.123.20.20",
            "expire_days": "30"
        }
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = host_serializers.HostCreateUpdateSerializer
    model = Host

    def create(self, request, *args, **kwargs):
        try:
            response = super(HostCreate, self).create(request, *args, **kwargs)
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


class HostUpdate(generics.RetrieveUpdateAPIView):
    """
    Updates registration for a host.

    **Required Arguments**:


    **Optional Arguments**:

    * `mac` -- A new MAC Address for the host.
    * `hostname` -- A new unique hostname.
    * `expire_days` -- Number of days until expiration.  Choices currently are:  1, 7, 14, 30, 180, 365
    * `pool`, `network`, or `ip_addresses` --  A pool name, network CIDR address, or ip address(es).
    * `ip_addresses` -- IP Addresses can be a single IP as a string or multiple IPs as a list.
    * `description` -- A text description of the host.
    * `dhcp_group` -- A DHCP Group id for this host.  Administrators Only.
    * `user_owners` -- A string or list or usernames to assign as owner to the host.
    * `group_owners` -- A string or list or group names to assign as owner to the host.

    **Example**:

        {
            "mac": "00:00:00:00:00:00",
            "hostname": "hostname.usu.edu",
            "ip_address": "129.123.20.20",
            "expire_days": "30"
        }
    """

    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)
    serializer_class = host_serializers.HostCreateUpdateSerializer
    queryset = Host.objects.all()

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except ValidationError as e:
            error_list = []
            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)
            return Response(
                {"non_field_errors": error_list}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)


class HostRenew(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)
    serializer_class = host_serializers.HostRenewSerializer
    queryset = Host.objects.all()

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class HostDelete(generics.DestroyAPIView):
    """
    Delete a host registration.

    All that is required for this to execute is calling it via a POST or DELETE request.
    """

    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)
    serializer_class = host_serializers.HostMacSerializer
    queryset = Host.objects.all()

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post_delete(self, obj):
        """
        Placeholder method for calling after deleting an object.
        """

    def perform_destroy(self, instance):
        instance.delete(user=self.request.user)


class HostBulkDelete(APIView):
    """
    Delete hosts from a from a list of mac addresses (mac_addr[])
    """

    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def post(self, request):
        if "mac_addr[]" not in request.data or not len(
            list(filter(lambda x: x, request.data.getlist("mac_addr[]")))
        ):
            return Response(
                {"error": "No host mac addresses(es) specified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Host.objects.filter(pk__in=request.data.getlist("mac_addr[]")).delete(
            request.user
        )

        return Response({"success": True}, status=status.HTTP_200_OK)


class BulkFixHostDNSRecords(APIView):
    """
    Attempts to re-populate a list of hosts' DNS records from their mac addresses (mac_addr[])
    """

    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def post(self, request):
        if "mac_addr[]" not in request.data or not len(
            list(filter(lambda x: x, request.data.getlist("mac_addr[]")))
        ):
            return Response(
                {"error": "Must specify mac addresses of hosts to populate"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hosts = Host.objects.filter(
            pk__in=request.data.getlist("mac_addr[]"),
            dns_records__isnull=True,
        )

        populate_record_status = []
        for host in hosts:
            try:
                dns_records = host.get_dns_records()
                if dns_records:
                    for record in dns_records:
                        record.host = host
                        record.changed_by = request.user
                        record.save()
                    continue

                host.delete_dns_records(user=request.user)
                host.add_dns_records(user=request.user)

                populate_record_status.append({"mac": str(host.mac), "success": True})
            except Exception as e:
                populate_record_status.append(
                    {"mac": str(host.mac), "success": False, "error": e}
                )

        return Response(populate_record_status, status=status.HTTP_200_OK)


class HostOwnerList(generics.RetrieveAPIView):
    serializer_class = host_serializers.HostOwnerSerializer
    queryset = Host.objects.all()


class HostOwnerAdd(APIView):
    """
    Adds owners for a host.

    **Arguments**:

    * `users` -- A list of usernames to add.
    * `groups` -- A list og group names to add.

    **Example**:

        {
            "users": ["user1", "user2"],
            "groups": ["group1", "group2"]
        }
    """

    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs["pk"])
        serializer = host_serializers.HostOwnerSerializer(data=request.data)

        if serializer.is_valid():
            user_list = serializer.data.get("users")
            group_list = serializer.data.get("groups")

            if user_list:
                users = User.objects.none()
                for username in user_list:
                    users |= User.objects.filter(username__iexact=username)

                for user in users:
                    assign_perm("hosts.is_owner_host", user, host)

            if group_list:
                groups = Group.objects.none()
                for groupname in group_list:
                    groups |= Group.objects.filter(name__iexact=groupname)

                for group in groups:
                    assign_perm("hosts.is_owner_host", group, host)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HostOwnerDelete(APIView):
    """
    Deletes owners for a host.

    **Arguments**:

    * `users` -- A list of usernames to delete.
    * `groups` -- A list og group names to delete.

    **Example**:

        {
            "users": ["user1", "user2"],
            "groups": ["group1", "group2"]
        }
    """

    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs["pk"])
        serializer = host_serializers.HostOwnerSerializer(data=request.data)
        if serializer.is_valid():
            user_list = serializer.data.get("users")
            group_list = serializer.data.get("groups")

            if user_list:
                users = User.objects.none()
                for username in user_list:
                    users |= User.objects.filter(username__iexact=username)

                for user in users:
                    remove_perm("hosts.is_owner_host", user, host)

            if group_list:
                groups = Group.objects.none()
                for groupname in group_list:
                    groups |= Group.objects.filter(name__iexact=groupname)

                for group in groups:
                    remove_perm("hosts.is_owner_host", group, host)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttributeList(generics.ListAPIView):
    serializer_class = host_serializers.AttributeListSerializer
    queryset = Attribute.objects.select_related().all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StructuredAttributeValueList(generics.ListAPIView):
    serializer_class = host_serializers.StructuredAttributeValueListSerializer
    queryset = StructuredAttributeValue.objects.select_related().all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("attribute__name", "value", "attribute")


class HostAttributeList(APIView):
    """
    Lists attributes for a host.
    """

    def get(self, request, format=None, **kwargs):
        attributes = {}
        host = get_object_or_404(Host, pk=kwargs["pk"])
        structured_attrs = StructuredAttributeToHost.objects.select_related(
            "structured_attribute_value", "structured_attribute_value__attribute"
        ).filter(host=host)
        freeform_attrs = FreeformAttributeToHost.objects.select_related(
            "attribute"
        ).filter(host=host)

        for attr in structured_attrs:
            attributes[
                attr.structured_attribute_value.attribute.name
            ] = attr.structured_attribute_value.value
        for attr in freeform_attrs:
            attributes[attr.attribute.name] = attr.value

        return Response(attributes, status=status.HTTP_200_OK)


class HostAddAttribute(APIView):
    """
    Adds or updates one or more attributes for a host.

    **Required arguments:**

    `attributes` -- a dictionary of attributes and values

    **Example:**

        {
            "attributes": {
                "border-profile": "server",
                "location": "some building"
            }
        }
    """

    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs["pk"])
        serializer = host_serializers.HostUpdateAttributeSerializer(data=request.data)
        if serializer.is_valid():
            attributes = serializer.data.get("attributes")
            # Get the DB attributes we are going to change
            db_attributes = Attribute.objects.filter(name__in=list(attributes.keys()))
            for attr in db_attributes:
                # Add structured attributes
                if attr.structured:
                    # delete existing attribute values
                    StructuredAttributeToHost.objects.filter(
                        host=host, structured_attribute_value__attribute=attr
                    ).delete()
                    value = attr.choices.get(value=attributes[attr.name])

                    # create selected attribute values
                    StructuredAttributeToHost.objects.create(
                        host=host,
                        structured_attribute_value=value,
                        changed_by=request.user,
                    )
                # Add freeform attributes
                else:
                    # FIXME: what about attributes that allow multiple values?
                    (
                        freeform_attr,
                        created,
                    ) = FreeformAttributeToHost.objects.get_or_create(
                        host=host,
                        attribute=attr,
                        defaults={
                            "changed_by": request.user,
                            "value": attributes[attr.name],
                        },
                    )
                    if not created:
                        freeform_attr.value = attributes[attr.name]
                        freeform_attr.changed_by = request.user
                        freeform_attr.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HostDeleteAttribute(APIView):
    """
    Deletes one or more attributes for a host.

    **Required arguments:**

    `attributes` -- a list of attribute keys

    **Example:**

        {
            "attributes": ["border-profile", "location"]
        }
    """

    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs["pk"])
        serializer = host_serializers.HostDeleteAttributeSerializer(data=request.data)

        if serializer.is_valid():
            attributes = serializer.data.get("attributes")
            # Get the DB attributes we are going to change
            db_attributes = Attribute.objects.filter(name__in=attributes)

            for attr in db_attributes:
                # Add structured attributes
                if attr.structured:
                    StructuredAttributeToHost.objects.filter(
                        host=host, structured_attribute_value__attribute=attr
                    ).delete()
                # Add freeform AttributeListSerializer
                else:
                    FreeformAttributeToHost.objects.filter(
                        host=host, attribute=attr
                    ).delete()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DisabledHostList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = host_serializers.DisabledHostListUpdateSerializer
    pagination_class = APIPagination
    queryset = (
        Disabled.objects.select_related("changed_by")
        .extra(
            select={
                "hostname": "SELECT hosts.hostname FROM hosts WHERE hosts.mac = disabled.mac"
            }
        )
        .all()
    )
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("changed_by__username",)


class DisabledHostCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    queryset = Disabled.objects.select_related("changed_by").all()
    serializer_class = host_serializers.DisabledHostListUpdateSerializer


class DisabledHostDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    queryset = Disabled.objects.all()
    serializer_class = host_serializers.DisabledHostDeleteSerializer

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
