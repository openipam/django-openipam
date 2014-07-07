from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import AllowAny

from openipam.dns.models import Domain, DnsRecord
from openipam.api.filters.dns import DomainFilter
from openipam.api.serializers.dns import DomainNameSerializer


class DomainNameList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    model = Domain
    serializer_class = DomainNameSerializer
    fields = ('name',)
    filter_fields = ('name', 'username')
    filter_class = DomainFilter
    paginate_by = 50
    paginate_by_param = 'limit'


class DomainList(generics.ListAPIView):
    model = Domain
    filter_fields = ('name', 'username')
    filter_class = DomainFilter
    paginate_by = 50
    paginate_by_param = 'limit'


