from openipam.hosts.models import (
    Host,
    Disabled as DisabledHostDetails,
    Attribute,
    StructuredAttributeToHost,
    FreeformAttributeToHost,
    GulRecentArpBymac,
    OUI,
)
from rest_framework import serializers
from openipam.network.models import Network, Pool, DhcpGroup, Address
from openipam.dns.models import Domain
from . import base as serializer_base
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
import re
from guardian.shortcuts import get_objects_for_user
from django.db.models import Q
from django.utils import timezone


class DisabledHostListSerializer(serializers.ModelSerializer):
    """
    Disabled Host serializer for list view.

    This is used for the disabled host list instead of the below
    DisabledHostSerializer because the DisabledHostSerializer
    doesn't contain any information about the host itself, only the
    disabled host details.
    """

    changed_by = serializer_base.ChangedBySerializer()
    mac = serializers.CharField()
    hostname = serializers.SerializerMethodField()
    disabled_host = serializers.SerializerMethodField()

    def get_disabled_host(self, obj):
        return True

    def get_hostname(self, obj):
        """
        Get hostname for host.

        Must be done this way because there isn't a foreign key constraint
        between DisabledHostDetails and Host. There is a reason for this: we
        want to be able to disable a host that doesn't exist in the database,
        or has been deleted. But it does make Django's ORM a little annoying
        to work with here.
        """
        try:
            host = Host.objects.get(mac=obj.mac)
            return host.hostname
        except Host.DoesNotExist:
            return None

    class Meta:
        model = DisabledHostDetails
        fields = (
            "reason",
            "changed",
            "changed_by",
            "mac",
            "hostname",
            "disabled_host",
        )


class DisabledHostSerializer(serializers.ModelSerializer):
    """
    Disabled Host serializer.

    Used for the disabled host details that are included in the HostSerializer.
    """

    changed_by = serializer_base.ChangedBySerializer()

    class Meta:
        model = DisabledHostDetails
        fields = (
            "reason",
            "changed",
            "changed_by",
        )

    def validate(self, data):
        """Validate data."""
        # Check if the user has permission to disable the host (add_disabled)
        if not self.context["request"].user.has_perm("hosts.add_disabled", self.context["host"]):
            raise serializers.ValidationError("You do not have permission to disable this host.")


class HostSerializer(serializers.ModelSerializer):
    """Host serializer."""

    disabled_host = DisabledHostSerializer()
    vendor = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    changed_by = serializer_base.ChangedBySerializer()
    dhcp_group = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    last_seen = serializers.DateTimeField(source="mac_history.stopstamp", read_only=True)
    last_seen_ip = serializers.CharField(source="mac_history.address_id.ip", read_only=True)
    address_type = serializers.CharField(source="address_type.name", read_only=True)

    def get_vendor(self, obj):
        oui = OUI.objects.filter(start__lt=obj.mac).filter(stop__gt=obj.mac)
        if oui.exists():
            return oui.first().shortname.split("\t")[-1]
        else:
            return None

    def get_details(self, obj):
        """Get a link to the host details page."""
        return self.context["request"].build_absolute_uri(f"/api/v2/hosts/{obj.mac}/")

    def get_dhcp_group(self, obj):
        """Get DHCP group for host."""
        if obj.dhcp_group:
            return {
                "id": obj.dhcp_group.id,
                "name": obj.dhcp_group.name,
                "description": obj.dhcp_group.description,
            }
        else:
            return None

    def get_addresses(self, obj):
        """Get addresses for host."""
        return {
            "leased": [
                str(lease.address)
                for lease in obj.leases.all()
                # Expired leases can be viewed at /leases/?show_expired, just show active leases here
                if lease.ends > timezone.now()
            ],
            "static": [str(address.address) for address in obj.addresses.all()],
        }

    def get_attributes(self, obj):
        """Get attributes for host."""

        # Get structured attributes
        structured_attrs = StructuredAttributeToHost.objects.filter(host=obj).select_related(
            "structured_attribute_value__attribute",
        )
        # Get freeform attributes
        freeform_attrs = FreeformAttributeToHost.objects.filter(host=obj).select_related("attribute")
        # Assemble a dictionary of all attributes
        attributes = {}
        for attr in structured_attrs:
            attributes[attr.structured_attribute_value.attribute.name] = attr.structured_attribute_value.value
        for attr in freeform_attrs:
            attributes[attr.attribute.name] = attr.value
        return attributes

    class Meta:
        """Meta class."""

        model = Host
        fields = (
            "mac",
            "details",
            "vendor",
            "hostname",
            "expires",
            "description",
            "is_dynamic",
            "disabled_host",
            "dhcp_group",
            "attributes",
            "addresses",
            "master_ip_address",
            "user_owners",
            "group_owners",
            "changed",
            "changed_by",
            "last_seen",
            "last_seen_ip",
            "address_type",
        )


class HostCreateUpdateSerializer(serializers.ModelSerializer):
    """Host create/update serializer.

    Due to technical limitations with django-rest-framework, this
    needs to be a separate serializer from the
    HostSerializer. Additionally, the data returned from this
    serializer is not the same as the HostSerializer. To populate the
    UI with the correct data after creating/updating a host, a UI
    will need to make a separate GET request to get the updated data.

    """

    mac = serializer_base.MACAddressField()
    expire_days = serializers.IntegerField(required=False, default=365)
    network = serializers.ChoiceField(choices=[], required=False, allow_blank=True)
    pool = serializers.ChoiceField(choices=[], required=False, allow_blank=True)
    ip_address = serializer_base.IPAddressField(required=False, allow_blank=True)
    dhcp_group = serializers.ChoiceField(choices=[], required=False, allow_blank=True)
    user_owners = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    group_owners = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)

    class Meta:
        model = Host
        fields = (
            "mac",
            "hostname",
            "expire_days",
            "description",
            "network",
            "pool",
            "ip_address",
            "dhcp_group",
            "user_owners",
            "group_owners",
        )

    def __init__(self, *args, **kwargs):
        super(HostCreateUpdateSerializer, self).__init__(*args, **kwargs)

        # Get all the networks that the current user has access to
        self.fields["network"].choices = [network.network for network in Network.objects.all()]
        self.fields["pool"].choices = [pool.name for pool in Pool.objects.all()]
        self.fields["dhcp_group"].choices = [group.name for group in DhcpGroup.objects.all()]

    def to_representation(self, instance):
        rep = super(HostCreateUpdateSerializer, self).to_representation(instance)
        rep["ip_address"] = instance.master_ip_address
        if instance.dhcp_group:
            rep["dhcp_group"] = instance.dhcp_group.name

        return rep

    def save(self):
        is_new = True if self.instance is None else False
        data = self.validated_data.copy()
        data["instance"] = self.instance
        data["user"] = self.context["request"].user
        self.instance = Host.objects.add_or_update_host(**data)

        LogEntry.objects.log_action(
            user_id=self.instance.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.instance).pk,
            object_id=self.instance.pk,
            object_repr=force_text(self.instance),
            action_flag=ADDITION if is_new else CHANGE,
            change_message="Host was added via API" if is_new else "Host was updated via API",
        )

    def validate(self, data):
        if not self.instance and not data.get("hostname"):
            raise serializers.ValidationError("Hostname is required.")
        if not self.instance and not data.get("ip_address") and not data.get("network") and not data.get("pool"):
            raise serializers.ValidationError("Either IP address, network or pool is required.")
        net_fields = set(["ip_address", "network", "pool"])
        attr_fields = set([key if value else None for key, value in list(data.items())])
        if len(net_fields.intersection(attr_fields)) > 1:
            raise serializers.ValidationError("Only one of IP address, network or pool can be specified.")
        return data

    def validate_expire_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Expire days must be positive.")

        if value > 365 and not self.context["request"].user.is_ipamadmin:
            raise serializers.ValidationError("Expire days cannot be greater than 365.")

        # Updater wants a string back
        return str(value)

    def validate_mac(self, value):
        mac = value
        mac = "".join([c for c in mac if re.match(r"[a-fA-F0-9]", c)])

        if len(mac) != 12:
            raise serializers.ValidationError("Invalid MAC address.")

        other_host = Host.objects.filter(mac=mac)
        if self.instance:
            other_host = other_host.exclude(mac=self.instance.pk)

        if other_host.exists():
            for host in other_host:
                if host.is_expired and host.is_disabled:
                    raise serializers.ValidationError(
                        f"Cannot register MAC {mac} because it is currently disabled."
                        + " Please contact the Service Desk for assistance."
                    )
                elif host.is_expired:
                    # Allow the new device owner to take over the expired host
                    host.delete(user=self.context["request"].user)
                else:
                    # Host is already registered
                    raise serializers.ValidationError(f"MAC {mac} is already registered as {host.hostname}.")
        return value

    def validate_hostname(self, value):
        hostname = value
        domain = value.split(".", 1)[-1]
        other_host = Host.objects.filter(hostname=hostname.lower())
        if self.instance:
            other_host = other_host.exclude(mac=self.instance.pk)

        if other_host.exists():
            for host in other_host:
                if host.is_expired:
                    # Allow a user to take over an expired hostname

                    # maybe we shouldn't allow this? this seems like a
                    # potential security issue
                    host.delete(user=self.context["request"].user)
                else:
                    # Hostname is already in use
                    raise serializers.ValidationError(f"Hostname {hostname} already points to {host.mac}.")

        # Validate that the user has permission to add a record to the domain
        user_domains = get_objects_for_user(
            self.context["request"].user,
            ["add_records_to_domain", "is_owner_domain"],
            Domain.objects.filter(name=domain),
            any_perm=True,
        )
        if not user_domains.exists():
            raise serializers.ValidationError(
                f"You do not have permission to use the domain {domain}. Please try a different domain."
            )
        return value

    def validate_network(self, value):
        network = value

        if network:
            try:
                network = Network.objects.get(network=network)
            except Network.DoesNotExist:
                raise serializers.ValidationError("Network is invalid.")

            user_pools = get_objects_for_user(
                self.context["request"].user,
                ["network.add_records_to_pool", "network.change_pool"],
                any_perm=True,
            )

            address = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True),
                network=network,
                host__isnull=True,
                reserved=False,
            ).order_by("address")

            if not address.exists():
                raise serializers.ValidationError("No available addresses in this network.")
        return network

    def validate_pool(self, value):
        pool = value
        if pool:
            user_pools = get_objects_for_user(
                self.context["request"].user,
                ["network.add_records_to_pool", "network.change_pool"],
                any_perm=True,
            )

            if pool not in [p.name for p in user_pools]:
                raise serializers.ValidationError("Pool is invalid.")

        return value

    def validate_ip_address(self, value):
        ip_address = value

        if ip_address:
            user_pools = get_objects_for_user(
                self.context["request"].user,
                ["network.add_records_to_pool", "network.change_pool"],
                any_perm=True,
            )
            user_nets = get_objects_for_user(
                self.context["request"].user,
                [
                    "network.add_records_to_network",
                    "network.change_network",
                    "network.is_owner_network",
                ],
                any_perm=True,
            )

            # check that address is free, and that we are allowed to use it
            addresses = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
                Q(leases__isnull=True) | Q(leases__ends__lte=timezone.now()) | Q(leases__abandoned=True),
                Q(host__isnull=True) | Q(host=self.instance),
                address=ip_address,
                reserved=False,
            ).values_list("address", flat=True)

            if ip_address not in map(str, addresses):
                raise serializers.ValidationError("The IP address is not available for use.")

        return value


class AttributeSerializer(serializers.Serializer):
    attributes = serializers.DictField(child=serializers.CharField())

    def validate_attributes(self, value):
        attributes = self.initial_data.get("attributes", {})
        print("attributes", attributes)
        for key, val in list(attributes.items()):
            attrs = Attribute.objects.filter(name=key)
            if not attrs.exists():
                raise serializers.ValidationError(f"Attribute {key} does not exist.")
            elif attrs.first().structured:
                choices = [choice.value for choice in attrs.first().choices.all()]
                if val not in choices:
                    raise serializers.ValidationError(
                        f"{val} is not a valid choice for {key}." f"Please specify one of {','.join(choices)}."
                    )
        return attributes

    def create(self, validated_data, host=None, user=None):
        print("creating attributes")
        if host is None:
            raise Exception("Host must be specified.")
        if user is None:
            raise Exception("User must be specified.")
        attributes = validated_data["attributes"]
        db_attrs = Attribute.objects.filter(name__in=list(attributes.keys()))
        for key, val in list(attributes.items()):
            attr = db_attrs.get(name=key)
            if attr.structured:
                # Structured attribute
                val = attr.choices.get(value=val)
                # Delete existing attribute values
                StructuredAttributeToHost.objects.filter(host=host, structured_attribute_value__attribute=attr).delete()
                # Create new attribute value
                StructuredAttributeToHost.objects.create(host=host, structured_attribute_value=val, changed_by=user)
            else:
                # Freeform attribute
                (
                    freeform_attr,
                    created,
                ) = FreeformAttributeToHost.objects.get_or_create(
                    host=host,
                    attribute=attr,
                    defaults={"changed_by": user, "value": val},
                )
                if not created:
                    freeform_attr.value = val
                    freeform_attr.changed_by = user
                    freeform_attr.save()

        return validated_data
