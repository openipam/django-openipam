from openipam.hosts.models import Host, Disabled
from rest_framework import serializers
from .users import UserNestedSerializer
from . import base as serializer_base
from django.utils import timezone
from django.db import connection


class DisabledHostSerializer(serializers.ModelSerializer):
    """Disabled Host serializer."""

    changed_by = serializer_base.ChangedBySerializer()

    class Meta:
        model = Disabled
        fields = (
            "reason",
            "changed",
            "changed_by",
        )


class HostSerializer(serializers.ModelSerializer):
    """Host serializer."""

    disabled_host = DisabledHostSerializer()
    addresses = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    owners = serializers.SerializerMethodField()
    changed_by = serializer_base.ChangedBySerializer()

    def get_addresses(self, obj):
        """Get addresses for host."""
        return {
            "leased": [
                {
                    "address": str(lease.address),
                    "starts": lease.starts,
                    "ends": lease.ends,
                    "abandoned": lease.abandoned,
                    "master": str(lease.address) == str(obj.master_ip_address),
                }
                for lease in obj.leases.all()  # [x for x in obj.leases.all() if x.ends > timezone.now()]
            ],
            "addresses": [
                {
                    "address": str(address.address),
                    "network": str(address.network),
                    "pool": address.pool,
                    "reserved": address.reserved,
                    "master": str(address.address) == str(obj.master_ip_address),
                }
                for address in obj.addresses.all()
            ],
        }

    def get_owners(self, obj):
        users, groups = obj.get_owners()
        return [
            {
                "username": owner.username,
                "first_name": owner.first_name,
                "last_name": owner.last_name,
                "email": owner.email,
            }
            for owner in users
        ] + [
            {
                "id": owner.id,
                "name": owner.name,
            }
            for owner in groups
        ]

    def get_attributes(self, obj):
        def dictfetchall(cursor):
            desc = cursor.description
            return [
                dict(list(zip([col[0] for col in desc], row)))
                for row in cursor.fetchall()
            ]

        c = connection.cursor()
        c.execute(
            """
            SELECT name, value from attributes_to_hosts WHERE mac = %s
            """,
            [str(obj.mac)],
        )

        rows = dictfetchall(c)
        return rows

    class Meta:
        model = Host
        fields = (
            "mac",
            "hostname",
            "expires",
            "description",
            "is_dynamic",
            "disabled_host",
            "dhcp_group",
            "attributes",
            "addresses",
            "master_ip_address",
            "owners",
            "changed",
            "changed_by",
        )


class HostCreateUpdateSerializer(serializers.ModelSerializer):
    """Host create/update serializer."""
