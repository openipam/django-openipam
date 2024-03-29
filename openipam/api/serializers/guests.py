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
    starts = serializers.DateField(format=None)
    ends = serializers.DateField(format=None)
    description = serializers.CharField(required=False)

    def validate_username(self, value):
        user = User.objects.filter(username__iexact=value)
        if not user:
            raise serializers.ValidationError("No User exists for username: %s" % value)

        return value

    def create(self, validated_data):
        instance = GuestTicket()
        instance.user = User.objects.get(
            username__iexact=validated_data.get("username")
        )
        instance.starts = validated_data.get("starts")
        instance.ends = validated_data.get("ends")
        instance.description = validated_data.get("description")
        instance.set_ticket()
        instance.save()

        return instance

    class Meta:
        model = GuestTicket
        fields = ("username", "user", "ticket", "starts", "ends", "description")


class GuestDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestTicket
        fields = ("user", "ticket", "starts", "ends", "description")
        read_only_fields = ("user", "ticket", "starts", "ends", "description")


class GuestRegisterSerializer(serializers.Serializer):
    name = serializers.CharField()
    ticket = serializers.CharField()
    ip_address = IPAddressField()
    mac_address = MACAddressField(required=False)
    description = serializers.CharField(required=False)

    def validate(self, data):
        mac_address = data.get("mac_address")

        if not mac_address:
            lease = Lease.objects.filter(address=data.get("ip_address")).first()
            if not lease:
                raise serializers.ValidationError(
                    [
                        "The MAC Address for this guest could not be found.",
                        "Ticket: %s, IP: %s"
                        % (data.get("ticket"), data.get("ip_address")),
                    ]
                )
            else:
                data["mac_address"] = lease.host_id

            host_exists = Host.objects.filter(
                mac=mac_address, expires__gte=timezone.now()
            ).first()
            if host_exists:
                raise serializers.ValidationError(
                    [
                        "The MAC Address for this guest is already registered on the network.",
                        "MAC: %s, IP: %s" % (mac_address, data.get("ip_address")),
                    ]
                )
        return data

    def validate_ticket(self, value):
        valid_ticket = GuestTicket.objects.filter(
            ticket=value, starts__lte=timezone.now(), ends__gte=timezone.now()
        ).first()

        if not valid_ticket:
            raise serializers.ValidationError(
                "Sponsor Code '%s' is expired or invalid" % value
            )

        self.valid_ticket = valid_ticket

        return value
