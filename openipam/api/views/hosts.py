from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions

from openipam.hosts.models import Host
from openipam.api.serializers.hosts import HostDetailSerializer, HostListSerializer, HostCreateUpdateSerializer
from openipam.api.filters.hosts import HostFilter

from django_filters import FilterSet, CharFilter, Filter


class HostList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Host.objects.prefetch_related('addresses').all()
    #model = Host
    serializer_class = HostListSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    filter_fields = ('mac', 'hostname', 'owner', 'group', 'is_expired')
    filter_class = HostFilter
    ordering_fields = ('expires', 'changed')
    ordering = ('expires',)
    paginate_by = 50


# class HostDetail(generics.RetrieveAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = HostDetailSerializer
#     model = Host


# class HostCreate(generics.CreateAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = HostCreateUpdateSerializer
#     model = Host


# class HostUpdate(generics.UpdateAPIView):
#     permissions = (permissions.IsAuthenticated,)
#     model = Host
