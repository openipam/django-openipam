from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.decorators import action, link
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status

from openipam.hosts.models import Host, StructuredAttributeToHost, FreeformAttributeToHost, Attribute
from openipam.api.serializers.hosts import HostDetailSerializer, HostListSerializer, HostCreateUpdateSerializer, \
    HostOwnerSerializer, HostUpdateAttributeSerializer, HostDeleteAttributeSerializer
from openipam.api.filters.hosts import HostFilter

from django_filters import FilterSet, CharFilter, Filter

from guardian.models import UserObjectPermission, GroupObjectPermission
from guardian.shortcuts import assign_perm, remove_perm

User = get_user_model()


class HostViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HostListSerializer
    queryset = Host.objects.prefetch_related('addresses', 'leases').all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    filter_fields = ('mac', 'hostname', 'owner', 'group', 'is_expired')
    filter_class = HostFilter
    ordering_fields = ('expires', 'changed')
    ordering = ('expires',)
    paginate_by = 50
    max_paginate_by = 5000


    def list(self, request, *args, **kwargs):
        return super(HostViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer = HostDetailSerializer
        return super(HostViewSet, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class HostList(generics.ListAPIView):
    """
        Lists hosts based on given criteria.

        **Optional Filters**

        * `mac` -- MAC Address contains
        * `hostname` -- Hostname contains
        * `user` -- Username of a user
        * `group` -- Group name of a group
        * `is_expired` -- 1 or 0 to see expired hosts
        * `limit` -- Number to enforce limit of records, default is 50, 0 shows all records (up to max of 5000).

        **Example**:

            /api/hosts/?group=switches&limit=0
    """

    permission_classes = (permissions.IsAuthenticated,)
    queryset = Host.objects.prefetch_related('addresses', 'leases').all()
    #model = Host
    serializer_class = HostListSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    filter_fields = ('mac', 'hostname', 'user', 'group', 'is_expired')
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


class HostDetail(generics.RetrieveAPIView):
    """
        Gets details for a host.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HostDetailSerializer
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
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HostCreateUpdateSerializer
    model = Host


class HostUpdate(generics.UpdateAPIView):
    """
        Updates registration for a host.

        **Required Arguments**:


        **Optional Arguments**:

        * `mac` -- A new MAC Address for the host.
        * `hostname` -- A new unique hostname.
        * `expire_days` -- Number of days until expiration.  Choices currently are:  1, 7, 14, 30, 180, 365
        * `pool`, `network`, or `ip_address` --  A pool name, network CIDR address, or ip address.
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
    permissions = (permissions.IsAuthenticated,)
    serializer_class = HostCreateUpdateSerializer
    model = Host

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class HostOwnerList(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HostOwnerSerializer
    model = Host


class HostOwnerAdd(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs['pk'])
        serializer = HostOwnerSerializer(data=request.DATA)

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
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs['pk'])
        serializer = HostOwnerSerializer(data=request.DATA)
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

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs['pk'])
        serializer = HostUpdateAttributeSerializer(data=request.DATA)
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

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None, **kwargs):
        host = get_object_or_404(Host, pk=kwargs['pk'])
        serializer = HostDeleteAttributeSerializer(data=request.DATA)

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


