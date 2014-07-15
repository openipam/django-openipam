from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers

from openipam.hosts.models import GuestTicket, Host
from openipam.network.models import Lease
from openipam.api.serializers.base import IPAddressField, MACAddressField

User = get_user_model()


class GuestTicketListCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    user = serializers.CharField(read_only=True)
    ticket = serializers.CharField(read_only=True)
    starts = serializers.DateField()
    ends = serializers.DateField()
    description = serializers.CharField(required=False)

    def validate_username(self, attrs, source):
        username = attrs.get(source)

        user = User.objects.filter(username__iexact=username)
        if not user:
            raise serializers.ValidationError("No User exists for username: %s" % username)

        return attrs

    def restore_object(self, attrs, instance=None):
        if not instance:
            instance = GuestTicket()
            instance.set_ticket()
        instance = super(GuestTicketListCreateSerializer, self).restore_object(attrs, instance)
        if attrs.get('username'):
            instance.user = User.objects.get(username__iexact=attrs['username'])

        return instance

    class Meta:
        model = GuestTicket


class GuestDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = GuestTicket
        fields = ('user', 'ticket', 'starts', 'ends', 'description')
        read_only_fields = ('user', 'ticket', 'starts', 'ends', 'description')


class GuestRegisterSerializer(serializers.Serializer):
    name = serializers.CharField()
    ticket = serializers.CharField()
    ip_address = IPAddressField()
    mac_address = MACAddressField(required=False)
    description = serializers.CharField(required=False)

    def validate_ticket(self, attrs, source):
        ticket = attrs.get(source)

        valid_ticket = GuestTicket.objects.filter(
            ticket=ticket,
            starts__lte=timezone.now(),
            ends__gte=timezone.now()
        ).first()

        if not valid_ticket:
            raise serializers.ValidationError("Sponsor Code '%s' is expired or invalid" % ticket)

        self.valid_ticket = valid_ticket

        return attrs

    def validate_mac_address(self, attrs, source):
        mac_address = attrs.get(source)

        if not mac_address:
            lease = Lease.objects.filter(address=attrs.get('ip_address')).first()
            if not lease:
                raise serializers.ValidationError(
                    "The MAC Address for this guest could not be found.",
                    "Ticket: %s, IP: %s" % (attrs.get('ticket'), attrs.get('ip_address'))
                )
            else:
                attrs['mac_address'] = lease.host_id

            host_exists = Host.objects.filter(mac=mac_address, expires__gte=timezone.now()).first()
            if host_exists:
                raise serializers.ValidationError(
                    "The MAC Address for this guest is already registered on the network.",
                    "MAC: %s, IP: %s" % (mac_address, attrs.get('ip_address'))
                )
        return attrs
