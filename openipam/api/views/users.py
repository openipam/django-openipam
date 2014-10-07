from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions

from openipam.api.permissions import IPAMAPIAdminPermission

User = get_user_model()


class UserList(generics.ListAPIView):
    model = User
    permission_classes = (permissions.IsAuthenticated, IPAMAPIAdminPermission)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('groups__name', 'username', 'email',)
