from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from openipam.hosts.models import Host, StructuredAttributeToHost, FreeformAttributeToHost, Attribute, StructuredAttributeValue
from openipam.network.models import Lease
from openipam.api.serializers import hosts as host_serializers
from openipam.api.filters.hosts import HostFilter
from openipam.api.permissions import IPAMChangeHostPermission

from guardian.shortcuts import assign_perm, remove_perm

User = get_user_model()


class HostList(generics.ListAPIView):
    """
        Lists hosts based on given criteria.

        **Optional Filters**

        * `mac` -- MAC Address contains
        * `hostname` -- Hostname contains
        * `user` -- Username of a user
        * `group` -- Group name of a group
        * `is_expired` -- 1 or 0 to see expired hosts
        * `ip_address` -- IP Address to filter on
        * `attribute` -- Name:Value to filter on attributes
        * `limit` -- Number to enforce limit of records, default is 50, 0 shows all records (up to max of 5000).

        **Example**:

            /api/hosts/?group=switches&limit=0
    """

    permission_classes = (IsAuthenticated,)
    queryset = Host.objects.prefetch_related('addresses', 'leases').all()
    serializer_class = host_serializers.HostListSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = HostFilter
    ordering_fields = ('expires', 'changed')
    ordering = ('expires',)
    paginate_by = 50
    max_paginate_by = 5000

    def get_paginate_by(self, queryset=None):
        #assert False, self.max_paginate_by
        param = self.request.QUERY_PARAMS.get(self.paginate_by_param)
        if param and param == '0':
            return self.max_paginate_by
        else:
            return super(HostList, self).get_paginate_by()


class HostMac(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        ip_address = request.GET.get('ip_address')
        leased_ip = request.GET.get('leased_ip')
        registered_ip = request.GET.get('registered_ip')
        host = None

        if ip_address:
            host = Host.objects.filter(
                Q(leases__address__address=ip_address) |
                Q(addresses__address=ip_address)
            ).first()

        elif leased_ip:
            lease = Lease.objects.filter(address=leased_ip).first()
            if lease:
                return Response({'mac': lease.host_id})

        elif registered_ip:
            host = Host.objects.filter(addresses__address=registered_ip).first()

        if host:
            return Response({'mac': host.mac})

        return Response({})


class HostNextMac(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        vendor = request.GET.get('vendor')

        if vendor:
            next_mac = Host.objects.find_next_mac(vendor)
            return Response(next_mac)

        return Response('')


class HostDetail(generics.RetrieveAPIView):
    """
        Gets details for a host.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = host_serializers.HostDetailSerializer
    model = Host


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
        except ValidationError, e:
            error_list = []
            if hasattr(e, 'error_dict'):
                for key, errors in e.message_dict.items():
                    for error in errors:
                        error_list.append('%s: %s' % (key.capitalize(), error))
            else:
                error_list.append(e.message)
            return Response({'non_field_errors': error_list}, status=status.HTTP_400_BAD_REQUEST)


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
        * `group_owners` -- A string or list or group names to assign as owner to the host.a

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
    model = Host

    def pre_save(self, obj):
        pass

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        self.object = self.get_object_or_none()

        serializer = self.get_serializer(self.object, data=request.DATA,
                                         files=request.FILES, partial=partial)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            if self.object is None:
                self.object = serializer.save(force_insert=True)
                self.post_save(self.object, created=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            self.object = serializer.save(force_update=True)
            self.post_save(self.object, created=False)
        except ValidationError, e:
            error_list = []
            if hasattr(e, 'error_dict'):
                for key, errors in e.message_dict.items():
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)
            return Response({'non_field_errors': error_list}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HostRenew(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)
    serializer_class = host_serializers.HostRenewSerializer
    model = Host

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class HostDelete(generics.DestroyAPIView):
    """
        Delete a host registration.

        All that is required for this to execute is calling it via a POST or DELETE request.
    """
    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)
    serializer_class = host_serializers.HostMacSerializer
    model = Host

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


    def post_delete(self, obj):
        """
        Placeholder method for calling after deleting an object.
        """
        pass


class HostOwnerList(generics.RetrieveAPIView):
    serializer_class = host_serializers.HostOwnerSerializer
    model = Host


class HostOwnerAdd(APIView):
    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs['pk'])
        serializer = host_serializers.HostOwnerSerializer(data=request.DATA)

        if serializer.is_valid():
            user_list = serializer.data.get('users')
            group_list = serializer.data.get('groups')

            if user_list:
                users = User.objects.none()
                for username in user_list:
                    users |= User.objects.filter(username__iexact=username)

                for user in users:
                    assign_perm('hosts.is_owner_host', user, host)

            if group_list:
                groups = Group.objects.none()
                for groupname in group_list:
                    groups |= Group.objects.filter(name__iexact=groupname)

                for group in groups:
                    assign_perm('hosts.is_owner_host', group, host)


            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HostOwnerDelete(APIView):
    permission_classes = (IsAuthenticated, IPAMChangeHostPermission)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs['pk'])
        serializer = host_serializers.HostOwnerSerializer(data=request.DATA)
        if serializer.is_valid():
            user_list = serializer.data.get('users')
            group_list = serializer.data.get('groups')

            if user_list:
                users = User.objects.none()
                for username in user_list:
                    users |= User.objects.filter(username__iexact=username)

                for user in users:
                    remove_perm('hosts.is_owner_host', user, host)

            if group_list:
                groups = Group.objects.none()
                for groupname in group_list:
                    groups |= Group.objects.filter(name__iexact=groupname)

                for group in groups:
                    remove_perm('hosts.is_owner_host', group, host)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttributeList(generics.ListAPIView):
    model = Attribute


class StructuredAttributeValueList(generics.ListAPIView):
    model = StructuredAttributeValue
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('attribute__name', 'value', 'attribute')


class HostAttributeList(APIView):
    """
        Lists attributes for a host.
    """

    def get(self, request, format=None, **kwargs):
        attributes = {}
        host = get_object_or_404(Host, pk=kwargs['pk'])
        structured_attrs = StructuredAttributeToHost.objects.select_related(
            'structured_attribute_value',
            'structured_attribute_value__attribute'
        ).filter(host=host)
        freeform_attrs = FreeformAttributeToHost.objects.select_related('attribute').filter(host=host)

        for attr in structured_attrs:
            attributes[attr.structured_attribute_value.attribute.name] = attr.structured_attribute_value.value
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
        host = get_object_or_404(Host, pk=kwargs['pk'])
        serializer = host_serializers.HostUpdateAttributeSerializer(data=request.DATA)
        if serializer.is_valid():
            attributes = serializer.data.get('attributes')
            # Get the DB attributes we are going to change
            db_attributes = Attribute.objects.filter(name__in=attributes.keys())
            for attr in db_attributes:
                # Add structured attributes
                if attr.structured:
                    existing_atts = StructuredAttributeToHost.objects.filter(
                        host=host,
                        structured_attribute_value__attribute=attr
                    ).delete()
                    value = attr.choices.get(value=attributes[attr.name])
                    structured_attr = StructuredAttributeToHost.objects.create(
                        host=host,
                        structured_attribute_value=value,
                        changed_by=request.user
                    )
                # Add freeform attributes
                else:
                    freeform_attr, created = FreeformAttributeToHost.objects.get_or_create(
                        host=host,
                        attribute=attr,
                    )
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
        host = get_object_or_404(Host, pk=kwargs['pk'])
        serializer = host_serializers.HostDeleteAttributeSerializer(data=request.DATA)

        if serializer.is_valid():
            attributes = serializer.data.get('attributes')
            # Get the DB attributes we are going to change
            db_attributes = Attribute.objects.filter(name__in=attributes)

            for attr in db_attributes:
                # Add structured attributes
                if attr.structured:
                    StructuredAttributeToHost.objects.filter(
                        host=host,
                        structured_attribute_value__attribute=attr
                    ).delete()
                # Add freeform attributes
                else:
                    FreeformAttributeToHost.objects.filter(
                        host=host,
                        attribute=attr,
                    ).delete()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

