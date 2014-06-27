from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions

from openipam.dns.models import Domain, DnsRecord
from openipam.api.filters.dns import DomainFilter


class DomainList(generics.ListAPIView):
    model = Domain
    filter_fields = ('name', 'username')
    filter_class = DomainFilter
    paginate_by = 50
    paginate_by_param = 'limit'


