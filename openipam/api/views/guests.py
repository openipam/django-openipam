from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView

from openipam.conf.ipam_settings import CONFIG
from openipam.hosts.models import GuestTicket, Host
from openipam.network.models import Pool
from openipam.api.views.base import APIMaxPagination
from openipam.api.serializers.guests import (
    GuestDeleteSerializer,
    GuestTicketListCreateSerializer,
    GuestRegisterSerializer,
)
from openipam.api.filters.guests import GuestTicketFilter
from openipam.api.permissions import IPAMGuestEnablePermission
from rest_framework.response import Response
from rest_framework import status

from django_pglocks import advisory_lock

User = get_user_model()


class GuestTicketList(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IPAMGuestEnablePermission)
    queryset = GuestTicket.objects.select_related().all()
    filter_class = GuestTicketFilter
    serializer_class = GuestTicketListCreateSerializer
    pagination_class = APIMaxPagination

    def list(self, request, *args, **kwargs):
        if not request.user.is_ipamadmin:
            self.queryset = GuestTicket.objects.filter(user=request.user)
        return super(GuestTicketList, self).list(request, *args, **kwargs)

    def get_paginate_by(self, queryset=None):
        param = self.request.QUERY_PARAMS.get(self.paginate_by_param)
        if param and param == "0":
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
    queryset = GuestTicket.objects.all()
    serializer_class = GuestDeleteSerializer
    lookup_field = "ticket"

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class GuestRegister(APIView):
    permission_classes = (AllowAny, IPAMGuestEnablePermission)

    def post(self, request, format=None, **kwargs):
        serializer = GuestRegisterSerializer(data=request.data)

        if serializer.is_valid():
            lock_id = "ipam-guest-register"

            with advisory_lock(lock_id):
                hostname_prefix = CONFIG.get("GUEST_HOSTNAME_FORMAT")[0]
                hostname_suffix = CONFIG.get("GUEST_HOSTNAME_FORMAT")[1]
                last_hostname = (
                    Host.objects.filter(
                        hostname__istartswith=hostname_prefix,
                        hostname__iendswith=hostname_suffix,
                    )
                    .extra(select={"hostname_length": "length(hostname)"})
                    .order_by("-hostname_length", "-hostname")
                    .first()
                )
                hostname_index = int(
                    last_hostname.hostname[
                        len(hostname_prefix) : last_hostname.hostname.find(
                            hostname_suffix
                        )
                    ]
                )
                guest_user = User.objects.get(username__iexact=CONFIG.get("GUEST_USER"))
                user_owner = serializer.valid_ticket.user
                description = serializer.data.get("description")
                name = serializer.data.get("name")
                ticket = serializer.data.get("ticket")
                mac_address = serializer.data.get("mac_address")

                try:
                    hostname = "%s%s%s" % (
                        hostname_prefix,
                        hostname_index + 1,
                        hostname_suffix,
                    )

                    # Check if instance already created.  Bug in DHCP thats registering it twice??
                    instance = Host.objects.filter(
                        hostname=hostname, mac=mac_address
                    ).first()

                    # Add or update host
                    Host.objects.add_or_update_host(
                        user=guest_user,
                        hostname=hostname,
                        mac=mac_address,
                        expires=serializer.valid_ticket.ends,
                        description=(
                            description
                            if description
                            else "Name: %s; Ticket used: %s" % (name, ticket)
                        ),
                        pool=Pool.objects.get(name=CONFIG.get("GUEST_POOL")),
                        user_owners=[user_owner],
                        group_owners=[CONFIG.get("GUEST_GROUP")],
                        instance=instance or None,
                    )
                except ValidationError as e:
                    error_list = []
                    if hasattr(e, "error_dict"):
                        for key, errors in list(e.message_dict.items()):
                            for error in errors:
                                error_list.append(error)
                    else:
                        error_list.append(e.message)
                    return Response(
                        {"non_field_errors": error_list},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            data = {
                "starts": serializer.valid_ticket.starts,
                "ends": serializer.valid_ticket.ends,
            }
            data.update(serializer.data)

            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
