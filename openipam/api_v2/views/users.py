from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from ..filters.users import UserFilterSet

from .base import APIPagination
from ..serializers.users import RestrictedUserSerializer, UserSerializer, GroupSerializer
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth.models import Group
from openipam.dns.models import Domain, DnsType
from openipam.hosts.models import Host
from openipam.network.models import Network, Pool

# Get the user model from Django
from django.contrib.auth import get_user_model

from guardian.shortcuts import assign_perm

User = get_user_model()

# from .base import APIModelViewSet, APIPagination


class UserView(generics.RetrieveAPIView):
    """API endpoint that allows users to be viewed."""

    permission_classes = [permissions.DjangoModelPermissions]
    # pagination_class = APIPagination
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, pk=None):
        serializer = UserSerializer(self.request.user)
        if not pk and self.request.user.is_authenticated:
            return Response(serializer.data)
        return Response(serializer.data)


class GroupView(generics.ListAPIView):
    """API endpoint that allows groups to be viewed."""

    permission_classes = [permissions.DjangoModelPermissions]
    pagination_class = APIPagination
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def filter_queryset(self, queryset):
        name = self.request.query_params.get("name", None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return super().filter_queryset(queryset)


class UserViewSet(viewsets.ModelViewSet):
    """Viewset for user objects. Does not allow user creation."""

    queryset = User.objects.prefetch_related("groups").all().order_by("-last_login")
    serializer_class = UserSerializer
    pagination_class = APIPagination
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    lookup_field = "username__iexact"
    filterset_class = UserFilterSet
    ordering_fields = ["username", "first_name", "last_name", "email", "is_active"]

    def get_serializer_class(self):
        """Use a restricted serializer for non-admin users."""
        if self.request.user.is_ipamadmin or self.action == "me":
            return self.serializer_class
        return RestrictedUserSerializer

    def get_queryset(self):
        """Only allow admins to list all users."""
        if not self.request.user.is_ipamadmin and self.action == "list":
            return self.queryset.filter(pk=self.request.user.pk)
        return self.queryset

    def create(self, request):
        """Create is not allowed, users are created via LDAP or shell."""
        return Response(status=405)

    def destroy(self, request, *args, **kwargs):
        """Destroy is not allowed, users are created via LDAP or shell."""
        return Response(status=405)

    def retrieve(self, request, username__iexact: str = None):
        """Return a single user by username."""
        username = username__iexact.lower()
        if username == self.request.user.username.lower():
            # Redirect to the "me" endpoint, which returns the current user with all fields
            # even if the user is not an admin.
            return Response(status=302, headers={"Location": self.reverse_action("me")})
        return super(UserViewSet, self).retrieve(request, username__iexact)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"me",
        url_name="me",
    )
    def me(self, request):
        """Return the current user."""
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"me/groups",
        url_name="my-groups",
    )
    def my_groups(self, request):
        """Return the current user."""
        user = self.request.user
        return Response(user.groups.values_list("name", flat=True))

    @action(
        detail=False,
        methods=["post"],
        url_path=r"assign-object-permissions",
        url_name="assign-object-permissions",
    )
    def assign_object_permissions(self, request):
        """Assign object permssions to given users."""
        users = self.request.data.get("users", [])
        object = self.request.data.get("object", None)
        permission = self.request.data.get("permission", [])
        if not users:
            return Response(status=400, data={"detail": "Users are required."})
        if not object:
            return Response(status=400, data={"detail": "Object is required."})
        if not permission:
            return Response(status=400, data={"detail": "Permission is required."})
        # assign object permission to users on object
        for user in users:
            try:
                user = User.objects.get(username=user)
                if "domain" in permission:
                    object = Domain.objects.get(name=object)
                elif "dnstype" in permission:
                    object = DnsType.objects.get(name=object)
                elif "host" in permission:
                    object = Host.objects.get(name=object)
                elif "network" in permission:
                    object = Network.objects.get(name=object)
                elif "pool" in permission:
                    object = Pool.objects.get(name=object)
                assign_perm(permission, user, object)
            except User.DoesNotExist:
                return Response(status=404, data={"detail": f"User {user} not found."})
            except Exception as e:
                return Response(status=500, data={"detail": f"Error: {e}"})
        return Response(status=201)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"groups",
        url_name="groups",
        permission_classes=[permissions.IsAdminUser],
    )
    def groups(self, request):
        """Return the current user."""
        username = request.query_params.get("username", None)
        if username is None:
            return Response(status=400, data={"detail": "Username is required."})
        user = self.queryset.get(username=username)
        return Response(user.groups.values_list("name", flat=True))

    @groups.mapping.post
    def groups_post(self, request):
        """Add the given user to the given groups."""
        username = request.data.get("username", None)
        if username is None:
            return Response(status=400, data={"detail": "Username is required."})
        user = self.queryset.get(username=username)
        groups = request.data.get("groups", [])
        print()
        print(groups)
        for group in groups:
            try:
                group = Group.objects.get(name=group)
                print()
                print(group)
                group.user_set.add(user)
                print()
                print(group)

            except Group.DoesNotExist:
                return Response(status=404, data={"detail": f"Group {group} not found."})
        return Response(user.groups.values_list("name", flat=True), status=201)

    @groups.mapping.delete
    def groups_delete(self, request):
        """Remove the user from the given groups."""
        username = request.data.get("username", None)
        if username is None:
            return Response(status=400, data={"detail": "Username is required."})
        user = self.queryset.get(username=username)
        groups = request.data.get("groups", [])
        for group in groups:
            try:
                Group.objects.get(name=group).user_set.remove(user)
            except Group.DoesNotExist:
                return Response(status=404, data={"detail": f"Group {group} not found."})
        return Response(user.groups.values_list("name", flat=True))
