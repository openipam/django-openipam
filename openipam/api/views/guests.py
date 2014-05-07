from django.contrib.auth import get_user_model

from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import filters
from rest_framework.views import APIView

from openipam.conf.ipam_settings import CONFIG
from openipam.hosts.models import GuestTicket, Host
from openipam.network.models import AddressType
from openipam.api.serializers.guests import GuestDeleteSerializer, GuestTicketListCreateSerializer, GuestRegisterSerializer
from openipam.api.filters.guests import GuestTicketFilter
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class GuestTicketList(generics.ListAPIView):
    queryset = GuestTicket.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = GuestTicketFilter
    serializer_class = GuestTicketListCreateSerializer
    paginate_by = 50
    max_paginate_by = 5000

    def list(self, request, *args, **kwargs):
        if not CONFIG.get('GUESTS_ENABLED', False):
            return Response({'detail': 'Guest access has been disabled.'}, status=status.HTTP_401_UNAUTHORIZED)
        return super(GuestTicketList, self).list(request, *args, **kwargs)

    def get_paginate_by(self, queryset=None):
        #assert False, self.max_paginate_by
        param = self.request.QUERY_PARAMS.get(self.paginate_by_param)
        if param and param == '0':
            return self.max_paginate_by
        else:
            return super(GuestTicketList, self).get_paginate_by()


class GuestTicketCreate(generics.CreateAPIView):
    queryset = GuestTicket.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = GuestTicketFilter
    serializer_class = GuestTicketListCreateSerializer

    def post(self, request, format=None, **kwargs):
        if not CONFIG.get('GUESTS_ENABLED', False):
            return Response({'detail': 'Guest access has been disabled.'}, status=status.HTTP_401_UNAUTHORIZED)
        return super(GuestTicketCreate, self).post(request, format, **kwargs)


class GuestTicketDelete(generics.RetrieveDestroyAPIView):
    serializer_class = GuestDeleteSerializer
    model = GuestTicket
    lookup_field = 'ticket'

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not CONFIG.get('GUESTS_ENABLED', False):
            return Response({'detail': 'Guest access has been disabled.'}, status=status.HTTP_401_UNAUTHORIZED)
        return super(GuestTicketDelete, self).destroy(request, *args, **kwargs)


class GuestRegister(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None, **kwargs):
        if not CONFIG.get('GUESTS_ENABLED', False):
            return Response({'detail': 'Guest access has been disabled.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = GuestRegisterSerializer(data=request.DATA)

        if serializer.is_valid():
            hostname_prefix = CONFIG.get('GUEST_HOSTNAME_FORMAT')[0]
            hostname_suffix = CONFIG.get('GUEST_HOSTNAME_FORMAT')[1]
            last_hostname = (Host.objects.filter(hostname__istartswith=hostname_prefix, hostname__iendswith=hostname_suffix)
                .extra(select={'hostname_length': 'length(hostname)'})
                .order_by('-hostname_length', '-hostname')
                .first()
            )
            hostname_index = int(last_hostname.hostname[len(hostname_prefix):last_hostname.hostname.find(hostname_suffix)])

            # Find the host or create a new one
            host = Host.objects.get_or_create(
                mac=serializer.data.get('mac_address')
            )
            # Set the guest hostname, desctription, expires and dynamic address type
            host.hostname = '%s%s%s' % (hostname_prefix, hostname_index+1, hostname_suffix)
            host.description = serializer.data.get('description', '')
            host.expires = serializer.data.get('ends')
            host.address_type_id = AddressType.objects.get(pool__name=CONFIG.get('GUEST_POOL'))
            host.save()

            # Set the pool relationships
            host.set_network_ip_or_pool()

            # Remove all previous woners and add 'guest' and ticket user as owners.
            host.remove_owners()
            host.assign_owner(User.objects.get(username__iexact=CONFIG.get('GUEST_USER')))
            host.assign_owner(request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


