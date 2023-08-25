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
from rest_framework import filters as rest_filters


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
    address_type = filters.CharFilter(
        method="filter_address_type", label="Address Type"
    )
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

    def filter_address_type(self, queryset, name, value):
        """Filter based on address type."""
        return queryset.filter(address_type_id=value)

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
        # Otherwise, search for partial matches.
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


class AdvancedSearchFilter(rest_filters.BaseFilterBackend):
    """
    Filter backend that implements the Advanced Search feature.

    Searches should be formatted as a comma-separated list of terms, where each term is
    formatted as <model>:<search term>. The search term is passed to the filter backend

    The choices for <model> are:
    - user (searches for users by username)
    - group (searches for groups by name)
    - net (searches for networks by CIDR block)
    - sattr (searches for structured attribute values by value)
    - atype (searches for address types by primary key)

    All searches are case-sensitive exact, and the value passed to this endpoint should be
    constructed based on the values selected from the autocomplete endpoint.
    """

    def _filter_users(self, queryset, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            return queryset.none()
        return get_objects_for_user(
            user,
            "hosts.is_owner_host",
            queryset,
            with_superuser=False,
            use_groups=False,
        )

    def _filter_groups(self, queryset, value):
        try:
            group = Group.objects.get(name=value)
        except Group.DoesNotExist:
            return queryset.none()
        return get_objects_for_group(group, "hosts.is_owner_host", queryset)

    def _filter_networks(self, queryset, value):
        # Use the net_contains_or_equals lookup so we don't have to hit the database
        # for each object.
        return queryset.filter(addresses__address__net_contains_or_equals=value)

    def _filter_sattr(self, queryset, value):
        return queryset.filter(
            structured_attributes__structured_attribute_value__value=value
        )

    def _filter_atype(self, queryset, value):
        return queryset.filter(address_type_id=value)

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset.
        """
        query_param = getattr(view, "advanced_search_param", "advanced_search")
        search_terms = request.query_params.get(query_param, "").split(",")

        for term in search_terms:
            if not term:
                continue
            try:
                model, value = term.split(":")
            except ValueError:
                continue
            if model == "user":
                queryset = self._filter_users(queryset, value)
            elif model == "group":
                queryset = self._filter_groups(queryset, value)
            elif model == "net":
                queryset = self._filter_networks(queryset, value)
            elif model == "sattr":
                queryset = self._filter_sattr(queryset, value)
            elif model == "atype":
                queryset = self._filter_atype(queryset, value)

        return queryset
