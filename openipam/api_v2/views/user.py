from openipam.user.models import User
from rest_framework import generics
from rest_framework.response import Response
from ..serializers.user import UserSerializer
from rest_framework import permissions

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
