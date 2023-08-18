from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from ..filters.dns import UserFilter

from .base import APIPagination
from ..serializers.users import RestrictedUserSerializer, UserSerializer
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# Get the user model from Django
from django.contrib.auth import get_user_model

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


class UserViewSet(viewsets.ModelViewSet):
    """Viewset for user objects. Does not allow user creation."""

    queryset = User.objects.prefetch_related("groups").all()
    serializer_class = UserSerializer
    pagination_class = APIPagination
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    lookup_field = "username__iexact"
    filterset_class = UserFilter
    ordering_fields = ["username", "first_name", "last_name", "email", "is_active"]

    def get_serializer_class(self):
        """Use a restricted serializer for non-admin users."""
        if self.request.user.is_superuser or self.action == "me":
            return self.serializer_class
        return RestrictedUserSerializer

    def get_queryset(self):
        """Only allow admins to list all users."""
        if not self.request.user.is_superuser and self.action == "list":
            return self.queryset.filter(pk=self.request.user.pk)
        return self.queryset

    def create(self, request):
        """Create is not allowed, users are created via LDAP or shell."""
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
