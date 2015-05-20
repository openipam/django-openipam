from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions

from openipam.api.permissions import IPAMAPIAdminPermission
from openipam.api.serializers.users import UserSerializer

User = get_user_model()


class UserList(generics.ListAPIView):
    queryset = User.objects.prefetch_related('user_permissions').all()
    permission_classes = (permissions.IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('groups__name', 'username', 'email',)
