"""Filters for hosts."""
from django_filters import rest_framework as filters
from openipam.hosts.models import Host, Disabled
from netfields import NetManager  # noqa
from guardian.shortcuts import get_objects_for_user, get_objects_for_group
from openipam.user.models import User
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db.models import Q
from ipaddress import ip_interface
from openipam.network.models import Lease


class HostFilter(filters.FilterSet):
    """Filter for hosts."""

    ip_address = filters.CharFilter(
        method="filter_ip_address", lookup_expr="icontains", label="IP Address"
    )
    dhcp_group = filters.CharFilter(
        method="filter_dhcp_group", lookup_expr="icontains", label="DHCP Group"
    )
    user = filters.CharFilter(
        method="filter_user", lookup_expr="icontains", label="User"
    )
    group = filters.CharFilter(
        method="filter_group", lookup_expr="icontains", label="Group"
    )
    mac = filters.CharFilter(
        method="filter_mac", lookup_expr="icontains", label="MAC Address"
    )
    hostname = filters.CharFilter(
        method="filter_hostname", lookup_expr="icontains", label="Hostname"
    )
    disabled = filters.BooleanFilter(method="filter_disabled", label="Disabled")
    # Expiration date filters
    expires__gt = filters.DateTimeFilter(method="filter_expires__gt", lookup_expr="gt")
    expires__lt = filters.DateTimeFilter(method="filter_expires__lt", lookup_expr="lt")

    def get_filterset_kwargs(self, request, queryset, view):
        kwargs = super().get_filterset_kwargs(request, queryset, view)

        # merge filterset kwargs provided by view class
        if hasattr(view, "get_filterset_kwargs"):
            kwargs.update(view.get_filterset_kwargs())

        return kwargs

    class Meta:
        model = Host
        fields = [
            "mac",
            "hostname",
            "ip_address",
            "dhcp_group",
            "user",
            "group",
            "expires__gt",
            "expires__lt",
        ]

    def filter_disabled(self, queryset, name, value):
        """Filter based on disabled."""
        # No foreign-key relationship to the disabled field (since unregistered MACs can be
        # disabled), so we have to do a subquery.
        if value:
            return queryset.filter(
                mac__in=Disabled.objects.values_list("mac", flat=True)
            )
        else:
            return queryset.exclude(
                mac__in=Disabled.objects.values_list("mac", flat=True)
            )

    def filter_expires__gt(self, queryset, name, value):
        return queryset.filter(expires__gte=value)

    def filter_expires__lt(self, queryset, name, value):
        return queryset.filter(expires__lte=value)

    def filter_mac(self, queryset, name, value):
        return queryset.filter(mac__istartswith=value)

    def filter_hostname(self, queryset, name, value):
        """Filter based on hostname."""
        return queryset.filter(hostname__icontains=value)

    def filter_user(self, queryset, name, value):
        """Filter based on user."""
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            return queryset.none()

        # This is an ownership search, not a permission check, so we don't want to
        # include superuser or group permissions.
        return get_objects_for_user(
            user,
            "hosts.is_owner_host",
            queryset,
            with_superuser=False,
            use_groups=False,
        )

    def filter_group(self, queryset, name, value):
        """Filter based on group."""
        try:
            group = Group.objects.get(name=value)
        except Group.DoesNotExist:
            return queryset.none()

        return get_objects_for_group(group, "hosts.is_owner_host", queryset)

    def filter_ip_address(self, queryset, name, value):
        """Filter based on IP address."""
        # Host IP addresses are stored in two different related tables, one for
        # static addresses and one for dynamic addresses. Additionally, we want to allow
        # searching for hosts by CIDR block, so we need to search both tables for
        # addresses that match the search term. We also need to filter out expired
        # leases.

        try:
            network = ip_interface(value).network
        except ValueError:
            pass
        else:
            valid_leases = Lease.objects.filter(
                starts__lte=timezone.now(),
                ends__gte=timezone.now(),
                address__address__net_contained=network,
            )
            return queryset.filter(
                Q(addresses__address__net_contained=network)
                | Q(
                    leases__pk__in=valid_leases,
                )
            )

        if value.count(".") == 3 and value[-1] != ".":
            # If the value is not a valid CIDR block, but is a valid IP address,
            # search for exact matches.
            valid_leases = Lease.objects.filter(
                starts__lte=timezone.now(),
                ends__gte=timezone.now(),
                address__address=value,
            )
            return queryset.filter(
                Q(addresses__address=value)
                | Q(
                    leases__pk__in=valid_leases,
                )
            )
        # Otherwise, search for partial matches. Add a trailing dot to the search if
        # it doesn't already have one.
        if value[-1] != ".":
            value = value + "."
        valid_leases = Lease.objects.filter(
            starts__lte=timezone.now(),
            ends__gte=timezone.now(),
            address__address__startswith=value,
        )
        return queryset.filter(
            Q(addresses__address__startswith=value)
            | Q(
                leases__pk__in=valid_leases,
            )
        )

    def filter_dhcp_group(self, queryset, name, value):
        """Filter based on DHCP group."""
        return queryset.filter(dhcp_group__name__icontains=value)
