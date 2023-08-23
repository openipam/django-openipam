"""Filters for network data."""
from functools import reduce
import django_filters as df
from netfields import NetManager  # noqa
from ipaddress import ip_interface, ip_address
from openipam.hosts.models import GulRecentArpByaddress, GulRecentArpBymac
from openipam.network.models import AddressType, Network, Address
from django.db.models import Q


class NetworkCIDRFilter(df.CharFilter):
    def __init__(self, *args, allow_ip_fragments=True, **kwargs):
        self.allow_ip_fragments = allow_ip_fragments
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        """Filter on network CIDR."""
        if not value:
            return qs.all()
        try:
            iface = ip_interface(value)
        except ValueError:
            if self.allow_ip_fragments:
                # Treat the input value as an IP address fragment, search for any networks that begin with it
                # Case-insensitive search is used to make IPv6 addresses more searchable if we ever
                # actually use them
                return qs.filter(**{f"{self.field_name}__istartswith": value})
            else:
                # Otherwise, return no results
                return qs.none()
        else:
            return qs.filter(
                **{f"{self.field_name}__{self.lookup_expr}": iface.network}
            )


class IPAddressFilter(df.CharFilter):
    def __init__(self, *args, allow_ip_fragments=False, **kwargs):
        self.allow_ip_fragments = allow_ip_fragments
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        """Filter on IP address."""
        if not value:
            return qs.all()
        try:
            addr = ip_address(value)
        except ValueError:
            if self.allow_ip_fragments:
                return qs.filter(**{f"{self.field_name}__istartswith": value})
            else:
                return qs.none()
        else:
            return qs.filter(**{f"{self.field_name}__{self.lookup_expr}": addr})


class NetworkFilter(df.FilterSet):
    """Filter for network objects."""

    network = NetworkCIDRFilter(
        field_name="network", lookup_expr="net_contained_or_equal", label="Network CIDR"
    )
    vlan_id = df.NumberFilter(
        field_name="vlan__vlan_id", lookup_expr="exact", label="VLAN ID"
    )
    vlan_name = df.CharFilter(
        field_name="vlan__name", lookup_expr="icontains", label="VLAN Name"
    )
    gateway = df.CharFilter(method="filter_gateway", label="Gateway IP")
    changed_by = df.CharFilter(
        field_name="changed_by__username", lookup_expr="iexact", label="Changed by"
    )
    name = df.CharFilter(field_name="name", lookup_expr="icontains", label="Name")
    address_type = df.ModelChoiceFilter(
        method="filter_address_type",
        queryset=AddressType.objects.all(),
        label="Address Type",
    )

    shared_network = df.CharFilter(
        field_name="shared_network__name",
        lookup_expr="icontains",
        label="Shared Network Name",
    )

    def filter_address_type(self, queryset, _, value):
        """Filter based on address type."""
        if value:
            ranges = value.ranges.all()
            if ranges:
                query = reduce(
                    lambda x, y: x | y,
                    [Q(network__net_contained_or_equal=r) for r in ranges],
                )
                queryset = queryset.filter(query)
            else:
                queryset = queryset.none()
        return queryset

    class Meta:
        model = Network
        fields = ["network", "vlan_id", "vlan_name", "gateway", "changed_by", "name"]


class AddressFilterSet(df.FilterSet):
    """Filter for address objects."""

    # We could relate this to the network table, but that would require a join,
    # and unless we have significant data integrity errors, searching by address
    # will have the same result as searching by network
    address = NetworkCIDRFilter(
        field_name="address",
        lookup_expr="net_contained_or_equal",
        label="Address in Network",
    )
    pool = df.CharFilter(
        field_name="pool__name", lookup_expr="icontains", label="Pool Name"
    )
    changed_by = df.CharFilter(
        field_name="changed_by__username", lookup_expr="iexact", label="Changed by"
    )
    host = df.CharFilter(
        field_name="host_id", lookup_expr="istartswith", label="Host MAC Address"
    )
    hostname = df.CharFilter(
        field_name="host__hostname", lookup_expr="icontains", label="Hostname"
    )
    last_seen__lt = df.DateFilter(
        method="filter_last_seen_before", label="Last Seen Before"
    )
    last_seen__gt = df.DateFilter(
        method="filter_last_seen_after", label="Last Seen After"
    )
    last_mac_seen = df.CharFilter(method="filter_last_mac_seen", label="Last MAC Seen")
    type = df.ModelChoiceFilter(
        method="filter_type",
        queryset=AddressType.objects.all(),
        label="Address Type",
    )

    def filter_type(self, queryset, _, value):
        """Filter based on address type."""
        if value:
            print(value)
            ranges = value.ranges.all()
            print(ranges)
            if ranges:
                query = reduce(
                    lambda x, y: x | y,
                    [Q(address__net_contained_or_equal=r) for r in ranges],
                )
                queryset = queryset.filter(query)
            else:
                queryset = queryset.none()
        return queryset

    def filter_last_mac_seen(self, queryset, _, value):
        """Filter based on last_mac_seen."""
        if value:
            queryset = queryset.filter(
                address__in=GulRecentArpBymac.objects.filter(host=value).values_list(
                    "address", flat=True
                )
            )
        return queryset

    def filter_last_seen_before(self, queryset, _, value):
        """Filter based on last_seen."""
        # Last seen is on the related (but not by foreign key) GulRecentArpByaddress table
        # They are linked by the address field.
        if value:
            queryset = queryset.filter(
                address__in=GulRecentArpByaddress.objects.filter(
                    stopstamp__lte=value
                ).values_list("address", flat=True)
            )
        return queryset

    def filter_last_seen_after(self, queryset, _, value):
        """Filter based on last_seen."""
        if value:
            queryset = queryset.filter(
                address__in=GulRecentArpByaddress.objects.filter(
                    stopstamp__gte=value
                ).values_list("address", flat=True)
            )
        return queryset

    class Meta:
        model = Address

        fields = [
            "address",
            "pool",
            "changed_by",
            "host",
            "hostname",
            "last_seen__lt",
            "last_seen__gt",
        ]
