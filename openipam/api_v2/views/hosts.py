"""Host API Views."""

from openipam.hosts.models import (
    Host,
    Disabled as DisabledHost,
    StructuredAttributeToHost,
    FreeformAttributeToHost,
)
from openipam.network import models as network_models
from openipam.user.models import User
from ..serializers import network as network_serializers
from ..serializers.hosts import (
    HostSerializer,
    HostCreateUpdateSerializer,
    DisabledHostSerializer,
    AttributeSerializer,
)
from ..filters.base import FieldSearchFilterBackend
from .. import permissions as api_permissions
from rest_framework import permissions as base_permissions, views
from .base import APIModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.core import exceptions as core_exceptions
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from guardian.shortcuts import get_objects_for_user
from netfields import NetManager  # noqa: F401 needed for net_contains


class HostViewSet(APIModelViewSet):
    """API endpoint that allows hosts to be viewed or edited."""

    queryset = Host.objects.prefetch_related("addresses", "leases", "pools").all()
    permission_classes = [
        api_permissions.HostPermission,
    ]
    filter_backends = [FieldSearchFilterBackend]
    search_fields = [
        ("mac", "mac"),
        ("hostname", "hostname"),
        ("master_ip_address", "ip_address"),
    ]

    def get_serializer_class(self):
        """Get serializer class."""
        if self.action in ["create", "update", "partial_update"]:
            return HostCreateUpdateSerializer
        return HostSerializer

    def perform_destroy(self, instance):
        """Perform destroy."""
        instance.delete(user=self.request.user)


class DisableView(views.APIView):
    """API endpoints for disabling and enabling hosts.

    GET to /hosts/<mac>/disabled/ to check if a host is disabled. Accessible to all users.
    POST to /hosts/<mac>/disabled/ to disable a host. Admins only.
    DELETE to /hosts/<mac>/disabled/ to enable a host. Admins only.

    Returns a JSON object with a "disabled" key, which is a boolean, as well as
    the following keys if the host is disabled:
    - "reason": The reason the host was disabled
    - "changed_by": The user who disabled the host
    - "changed_at": The time the host was disabled
    """

    permission_classes = [
        base_permissions.DjangoModelPermissions,
    ]
    queryset = DisabledHost.objects.all()

    def post(self, request, *args, **kwargs):
        """Post."""
        mac = kwargs["mac"]
        reason = request.data.get("reason", "No reason given")
        disabled = DisabledHost.objects.create(
            mac=mac, reason=reason, changed_by=request.user
        )
        serializer = DisabledHostSerializer(disabled)
        data = serializer.data.copy()
        data["disabled"] = True

        try:
            host = Host.objects.get(mac=mac)
        except Host.DoesNotExist:
            message = f"Disabled host {mac}"
        else:
            message = f"Disabled host {host.mac} ({host.hostname})"

        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(disabled).pk,
            object_id=disabled.pk,
            object_repr=disabled.mac,
            action=ADDITION,
            change_message=message,
        )

        return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Delete."""
        mac = kwargs["mac"]
        disabled = get_object_or_404(DisabledHost, mac=mac)
        disabled.delete()
        data = {"disabled": False}

        try:
            host = Host.objects.get(mac=mac)
        except Host.DoesNotExist:
            message = f"Enabled host {mac}"
        else:
            message = f"Enabled host {host.mac} ({host.hostname})"

        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(disabled).pk,
            object_id=disabled.pk,
            object_repr=disabled.mac,
            action=DELETION,
            change_message=message,
        )
        return Response(data)

    def get(self, request, *args, **kwargs):
        """Get."""
        mac = kwargs["mac"]
        disabled = DisabledHost.objects.filter(mac=mac)
        if not disabled.exists():
            return Response({"disabled": False})
        serializer = DisabledHostSerializer(disabled)
        data = serializer.data.copy()
        data["disabled"] = True
        return Response(data)


class UserOwnerView(views.APIView):
    """
    API endpoints for manipulating host ownership.

    GET to /hosts/<mac>/users/ to list all users who own a host. Accessible to all users.
    POST to /hosts/<mac>/users/ to add a user as an owner of a host. Owners only.
    DELETE to /hosts/<mac>/users/ to clear all owners of a host. Admins only.
    PUT to /hosts/<mac>/users/ to replace all owners of a host. Owners only.

    Above endpoint returns a JSON array of usernames, e.g. ["user1", "user2"], except for DELETE,
    which returns 204 No Content. POST and PUT take a JSON array of usernames, e.g. ["user1", "user2"].

    GET to /hosts/<mac>/users/<username>/ to check if a user owns a host. Accessible to all users.
    DELETE to /hosts/<mac>/users/<username>/ to remove a user as an owner of a host. Owners only.

    GET returns a boolean, e.g. true or false. DELETE returns the same JSON array as above.
    """

    permission_classes = [
        api_permissions.HostPermission,
    ]

    def post(self, request, *args, **kwargs):
        """Post."""
        self.action = "create"
        mac = kwargs["mac"]
        username = kwargs.get("username")
        if username is not None:
            return Response(
                {"detail": f"Cannot POST to /hosts/{mac}/users/{username}/"}, status=405
            )
        host = get_object_or_404(Host, mac=mac)
        self.check_object_permissions(request, host)
        for username in request.data:
            user = get_object_or_404(User, username=username)
            # Check permissions
            # Create ownership record
            host.assign_owner(user)
        # Update changedby field
        host.save(user=request.user)
        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(host).pk,
            object_id=host.pk,
            object_repr=str(host.mac),
            action=CHANGE,
            change_message=f"Added users {', '.join(request.data)} as owners",
        )
        return Response(host.user_owners)

    def get(self, request, *args, **kwargs):
        """Get."""
        self.action = "list"
        mac = kwargs["mac"]
        username = kwargs.get("username")
        if username is not None:
            host = get_object_or_404(Host, mac=mac)
            serializer = HostSerializer(host)
            return Response(username in serializer.data.get("user_owners"))
        host = get_object_or_404(Host, mac=mac)
        serializer = HostSerializer(host)
        return Response(serializer.data.get("user_owners"))

    def delete(self, request, *args, **kwargs):
        """Delete."""
        self.action = "destroy"
        mac = kwargs["mac"]
        username = kwargs.get("username")
        if username is None and not request.user.is_ipamadmin:
            return Response(
                {"detail": "Cannot DELETE to /hosts/<mac>/users/"}, status=405
            )
        elif request.user.is_ipamadmin:
            host = get_object_or_404(Host, mac=mac)
            # User is admin, no need to check permissions
            # Delete ownership records
            host.remove_user_owners()
            # Update changedby field
            host.save(user=request.user)
            # Log the event
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=str(host.mac),
                action=CHANGE,
                change_message=f"Removed all user owners",
            )
            return Response(status=204)
        user = get_object_or_404(User, username=username)
        host = get_object_or_404(Host, mac=mac)
        # Check permissions
        self.check_object_permissions(request, host)
        # Delete ownership record
        host.remove_owner(user)
        # Update changedby field
        host.save(user=request.user)
        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(host).pk,
            object_id=host.pk,
            object_repr=str(host.mac),
            action=CHANGE,
            change_message=f"Removed user {user.username} as owner",
        )
        return Response(host.user_owners)

    def put(self, request, *args, **kwargs):
        """Put."""
        self.action = "update"
        mac = kwargs["mac"]
        username = kwargs.get("username")
        if username is not None:
            return Response(
                {"detail": "Cannot PUT to /hosts/<mac>/users/<username>/"}, status=405
            )
        host = get_object_or_404(Host, mac=mac)
        # Check permissions
        self.check_object_permissions(request, host)
        # Replace ownership records
        host.remove_user_owners()
        for username in request.data:
            user = get_object_or_404(User, username=username)
            host.assign_owner(user)
        # Update changedby field
        host.save(user=request.user)
        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(host).pk,
            object_id=host.pk,
            object_repr=str(host.mac),
            action=CHANGE,
            change_message=f"Replaced user owners with {', '.join(request.data)}",
        )
        return Response(host.user_owners)


class GroupOwnerView(views.APIView):
    """
    API endpoints for manipulating host ownership, group version.

    GET to /hosts/<mac>/groups/ to list all groups who own a host. Accessible to all users.
    POST to /hosts/<mac>/groups/ to add a group as an owner of a host. Owners only.
    DELETE to /hosts/<mac>/groups/ to clear all group owners of a host. Admins only.
    PUT to /hosts/<mac>/groups/ to replace all group owners of a host. Owners only.

    Above endpoint returns a JSON array of group names, e.g. ["group1", "group2"], except for DELETE,
    which returns 204 No Content. POST and PUT take a JSON array of group names, e.g. ["group1", "group2"].

    GET to /hosts/<mac>/groups/<groupname>/ to check if a group owns a host. Accessible to all users.
    DELETE to /hosts/<mac>/groups/<groupname>/ to remove a group as an owner of a host. Owners only.

    GET returns a boolean, e.g. true or false. DELETE returns the same JSON array as above.
    """

    permission_classes = [
        api_permissions.HostPermission,
    ]

    def post(self, request, *args, mac, **kwargs):
        """Post."""
        groupname = kwargs.get("groupname")
        if groupname is not None:
            return Response(
                {"detail": f"Cannot POST to /hosts/{mac}/groups/{groupname}/"},
                status=405,
            )
        host = get_object_or_404(Host, mac=mac)
        # Check permissions
        self.check_object_permissions(request, host)
        for group in request.data:
            group = get_object_or_404(Group, name=group)
            # Create ownership record
            host.assign_owner(group)
        # Update the changedby field
        host.save(user=request.user)
        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(host).pk,
            object_id=host.pk,
            object_repr=str(host.mac),
            action=CHANGE,
            change_message=f"Added groups {', '.join(request.data)} as owners",
        )
        return Response(host.group_owners)

    def get(self, request, *args, mac, groupname=None, **kwargs):
        """Get."""
        host = get_object_or_404(Host, mac=mac)
        if groupname is not None:
            return Response(groupname in host.group_owners)
        return Response(host.group_owners)

    def delete(self, request, *args, mac, groupname=None, **kwargs):
        """Delete."""
        host = get_object_or_404(Host, mac=mac)
        if groupname is None and not request.user.is_ipamadmin:
            return Response(
                {"detail": f"Cannot DELETE to /hosts/{mac}/groups/"}, status=405
            )
        elif request.user.is_ipamadmin:
            # User is admin, no need to check permissions
            # Delete ownership records
            host.remove_group_owners()
            # Update the changedby field
            host.save(user=request.user)
            # Log the event
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=str(host.mac),
                action=CHANGE,
                change_message=f"Removed all group owners",
            )
            return Response(status=204)
        group = get_object_or_404(Group, name=groupname)
        # Check permissions
        self.check_object_permissions(request, host)
        # Delete ownership record
        host.remove_owner(group)
        # Update the changedby field
        host.save(user=request.user)
        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(host).pk,
            object_id=host.pk,
            object_repr=str(host.mac),
            action=CHANGE,
            change_message=f"Removed group {group.name} as owner",
        )
        return Response(host.group_owners)

    def put(self, request, *args, mac, username=None, **kwargs):
        """Put."""
        if username is not None:
            return Response(
                {"detail": f"Cannot PUT to /hosts/{mac}/groups/{username}/"},
                status=405,
            )
        host = get_object_or_404(Host, mac=mac)
        # Check permissions
        self.check_object_permissions(request, host)
        # Replace ownership records
        host.remove_group_owners()
        for groupname in request.data:
            group = get_object_or_404(Group, name=groupname)
            host.assign_owner(group)
        # Update the changedby field
        host.save(user=request.user)
        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(host).pk,
            object_id=host.pk,
            object_repr=str(host.mac),
            action=CHANGE,
            change_message=f"Replaced group owners with {', '.join(request.data)}",
        )
        return Response(host.group_owners)


class HostAttributesView(views.APIView):
    """
    View and manipulate attributes on a given host.

    GET to /hosts/<mac>/attributes/ to list all attributes on a host. Accessible to all users.
    POST to /hosts/<mac>/attributes/ to add attributes to a host. Owners only.
    DELETE to /hosts/<mac>/attributes/ to clear all attributes from a host. Owners only.
    """

    permission_classes = [
        api_permissions.HostPermission,
    ]

    def get(self, request, *args, mac, **kwargs):
        """Get."""
        host = get_object_or_404(Host, mac=mac)
        structured_attrs = StructuredAttributeToHost.objects.select_related(
            "structured_attribute_value", "structured_attribute_value__attribute"
        ).filter(host=host)
        freeform_attrs = FreeformAttributeToHost.objects.select_related(
            "attribute"
        ).filter(host=host)
        attributes = {}
        for attr in structured_attrs:
            attributes[
                attr.structured_attribute_value.attribute.name
            ] = attr.structured_attribute_value.value
        for attr in freeform_attrs:
            attributes[attr.attribute.name] = attr.value
        return Response(attributes, status=status.HTTP_200_OK)

    def post(self, request, *args, mac, **kwargs):
        """Post."""
        host = get_object_or_404(Host, mac=mac)
        # Check permissions
        self.check_object_permissions(request, host)
        # Create attribute
        serializer_data = {"attributes": request.data}
        print(serializer_data)
        serializer = AttributeSerializer(data=serializer_data)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.create(serializer.validated_data, host=host, user=request.user)
            # Return the updated list of attributes
            response = self.get(request, *args, mac=mac, **kwargs)
            response.status_code = status.HTTP_201_CREATED
            # Log the event
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=str(host.mac),
                action=CHANGE,
                change_message=f"Set attributes: {request.data}",
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, mac, **kwargs):
        """Patch."""
        # POST already performs partial updates, so just call that.
        return self.post(request, *args, mac, **kwargs)

    def delete(self, request, *args, mac, **kwargs):
        """Delete."""
        host = get_object_or_404(Host, mac=mac)
        # Check permissions
        self.check_object_permissions(request, host)
        # Delete attributes
        host.freeform_attributes.all().delete()
        host.structured_attributes.all().delete()
        host.save(user=request.user)
        # Log the event
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(host).pk,
            object_id=host.pk,
            object_repr=str(host.mac),
            action=CHANGE,
            change_message=f"Cleared all attributes",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddressView(views.APIView):
    """View and manipulate host addresses."""

    permission_classes = [
        # Make sure the user is authenticated, but leave other
        # permissions checks to the view methods
        base_permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        """Return the queryset for this view."""
        # Only return addresses that are assigned to this host
        return network_models.Address.objects.filter(host=self.kwargs["mac"])

    def get(self, request, *args, mac, host=None, **kwargs):
        """Get."""
        if kwargs.get("address") is not None:
            # Can't GET a specific address
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        host = host or get_object_or_404(Host, mac=mac)
        addresses = host.addresses.all()
        serializer = network_serializers.AddressSerializer(addresses, many=True)
        data = serializer.data
        for address in data:
            address["network"] = str(address["network"])
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, mac, **kwargs):
        """Post."""
        if kwargs.get("address") is not None:
            # Can't POST to a specific address
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        host = get_object_or_404(Host, mac=mac)
        address = request.data.get("address")
        hostname = request.data.get("hostname")
        if address is None:
            return Response(
                {"detail": "address must be specified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if hostname is None:
            return Response(
                {"detail": "hostname must be specified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check permissions
        if not api_permissions.HostPermission().has_object_permission(
            request, self, host
        ):
            return Response(
                {"detail": "You do not have permission to add addresses to this host."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Get the user's allowed networks and pools
        user_pools = get_objects_for_user(
            request.user,
            ["network.add_records_to_pool", "network.change_pool"],
            any_perm=True,
        )
        user_networks = get_objects_for_user(
            request.user,
            [
                "network.add_records_to_network",
                "network.change_network",
                "network.is_owner_network",
            ],
            any_perm=True,
        )

        # Check if we are allowed to use the address. Let the host model
        # handle the availability check.
        address_objs = network_models.Address.objects.filter(
            Q(pool__in=user_pools) | Q(network__in=user_networks),
            address=address,
        ).values_list("address", flat=True)

        if address not in map(str, address_objs):
            return Response(
                {"detail": "You do not have permission to use this address."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            host.add_address(user=request.user, ip_address=address, hostname=hostname)
        except core_exceptions.ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Log the event
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=str(host.mac),
                action=CHANGE,
                change_message=f"Added address {address}",
            )

        # Return the updated list of addresses
        return self.get(request, mac=mac, host=host)

    def delete(self, request, *args, mac, address=None, **kwargs):
        """Delete."""
        if address is None:
            # wrong endpoint, <mac>/addresses does not support DELETE
            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        host = get_object_or_404(Host, mac=mac)
        # Check permissions
        if not api_permissions.HostPermission().has_object_permission(
            request, self, host
        ):
            return Response(
                {
                    "detail": "You do not have permission to remove addresses from this host."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            host.delete_address(request.user, address)
        except core_exceptions.ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Log the event
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=str(host.mac),
                action=CHANGE,
                change_message=f"Removed address {address}",
            )

        # Return the updated list of addresses
        return self.get(request, mac=mac, host=host)


class LeasesView(views.APIView):
    """View active and historical leases."""

    # Lease data is not sensitive, the existing frontend does not
    # restrict access to a device's leases. We'll add a permission
    # check for viewing historical data, but leave the active leases
    # view open to all authenticated users.
    permission_classes = [
        base_permissions.IsAuthenticated,
    ]

    def get(self, request, *args, mac, **kwargs):
        """Get."""
        host = get_object_or_404(Host, mac=mac)
        leases = host.leases.all()
        # If the user asks for expired leases, return them all
        if request.query_params.get("show_expired") is None:
            leases = leases.filter(ends__gt=timezone.now())
        elif not api_permissions.HostPermission().has_object_permission(
            request, self, host, check_for_read=True
        ):
            # If the user asks for expired leases and does not have
            # permission to view historical data, restrict them to
            # active ones anyways.
            leases = leases.filter(ends__gt=timezone.now())
        leases = leases.order_by("-ends")
        leases = leases.select_related("address", "address__network")
        data = [
            {
                "address": network_serializers.AddressSerializer(lease.address).data,
                "abandoned": lease.abandoned,
                "starts": lease.starts,
                "ends": lease.ends,
                "server": lease.server,
                "active": lease.ends > timezone.now(),
            }
            for lease in leases
        ]
        return Response(data, status=status.HTTP_200_OK)
