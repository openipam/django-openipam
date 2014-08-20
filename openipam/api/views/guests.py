from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework import filters
from rest_framework.views import APIView

from openipam.conf.ipam_settings import CONFIG
from openipam.hosts.models import GuestTicket, Host
from openipam.network.models import AddressType, Pool
from openipam.api.serializers.guests import GuestDeleteSerializer, GuestTicketListCreateSerializer, GuestRegisterSerializer
from openipam.api.filters.guests import GuestTicketFilter
from openipam.api.permissions import IPAMGuestEnablePermission
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class GuestTicketList(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IPAMGuestEnablePermission)
    queryset = GuestTicket.objects.all()
    filter_class = GuestTicketFilter
    serializer_class = GuestTicketListCreateSerializer
    paginate_by = 50
    max_paginate_by = 5000

    def list(self, request, *args, **kwargs):
        if not request.user.is_ipamadmin:
            self.queryset = GuestTicket.objects.filter(user=request.user)
        return super(GuestTicketList, self).list(request, *args, **kwargs)

    def get_paginate_by(self, queryset=None):
        #assert False, self.max_paginate_by
        param = self.request.QUERY_PARAMS.get(self.paginate_by_param)
        if param and param == '0':
            return self.max_paginate_by
        else:
            return super(GuestTicketList, self).get_paginate_by()


class GuestTicketCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IPAMGuestEnablePermission)
    queryset = GuestTicket.objects.all()
    filter_class = GuestTicketFilter
    serializer_class = GuestTicketListCreateSerializer


class GuestTicketDelete(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated, IPAMGuestEnablePermission)
    serializer_class = GuestDeleteSerializer
    model = GuestTicket
    lookup_field = 'ticket'

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class GuestRegister(APIView):
    permission_classes = (AllowAny, IPAMGuestEnablePermission)

    def post(self, request, format=None, **kwargs):
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
            guest_user = User.objects.get(username__iexact=CONFIG.get('GUEST_USER'))
            user_owner = serializer.valid_ticket.user
            description = serializer.data.get('description')
            name = serializer.data.get('name')
            ticket = serializer.data.get('ticket')
            mac_address = serializer.data.get('mac_address')

            try:
                # Add or update host
                Host.objects.add_or_update_host(
                    user=guest_user,
                    hostname='%s%s%s' % (hostname_prefix, hostname_index+1, hostname_suffix),
                    mac=mac_address,
                    expires=serializer.valid_ticket.ends,
                    description=description if description else 'Name: %s; Ticket used: %s' % (name, ticket),
                    pool=Pool.objects.get(name=CONFIG.get('GUEST_POOL')),
                    user_owners=[user_owner],
                    group_owners=[CONFIG.get('GUEST_GROUP')]
                )
            except ValidationError as e:
                error_list = [
                    'There has been an error processing your request',
                    'Please contact an Administrator.'
                ]
                if hasattr(e, 'error_dict'):
                    for key, errors in e.message_dict.items():
                        for error in errors:
                            error_list.append(error)
                else:
                    error_list.append(e.message)
                return Response({'non_field_errors': error_list}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'starts': serializer.valid_ticket.starts,
                'ends': serializer.valid_ticket.ends
            }
            data.update(serializer.data)

            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
