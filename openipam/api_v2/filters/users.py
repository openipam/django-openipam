# import Concat from django
from rest_framework import filters
import django_filters as df
from django.contrib.auth import get_user_model
from django.db.models import functions as dfn, Q

User = get_user_model()


class UserFilterSet(df.FilterSet):
    """Filterset for users."""

    username = df.CharFilter(lookup_expr="icontains", label="Username")
    full_name = df.CharFilter(method="filter_full_name", label="Full Name")
    email = df.CharFilter(lookup_expr="icontains", label="Email")
    groups = df.CharFilter(method="filter_groups", label="Groups")
    is_active = df.BooleanFilter(label="Active")
    is_staff = df.BooleanFilter(label="Staff")
    is_superuser = df.BooleanFilter(label="Superuser")
    is_ipamadmin = df.BooleanFilter(label="IPAM Admin", method="filter_is_ipamadmin")
    source = df.CharFilter(method="filter_source", label="Source")

    def filter_source(self, queryset, _, value):
        """Filter based on source."""
        if value:
            return queryset.filter(source__name__iexact=value)
        else:
            return queryset

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "groups",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

    def filter_is_ipamadmin(self, queryset, _, value):
        """Filter based on is_ipamadmin."""
        if value:
            return queryset.filter(Q(groups__name__iexact="ipam-admins") | Q(is_superuser=True)).distinct()
        else:
            return queryset.exclude(Q(groups__name__iexact="ipam-admins") | Q(is_superuser=True)).distinct()

    def filter_full_name(self, queryset, _, value):
        """Filter based on full name."""
        if value:
            queryset = queryset.annotate(
                full_name=dfn.Concat(
                    "first_name",
                    dfn.Value(" "),
                    "last_name",
                    output_field=dfn.CharField(),
                )
            ).filter(full_name__icontains=value)
        return queryset

    def filter_groups(self, queryset, _, value):
        """Filter based on groups."""
        if value:
            queryset = queryset.filter(groups__name__iexact=value)
        return queryset


class AdvancedSearchFilter(filters.BaseFilterBackend):
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

    def _filter_permissions(self, queryset, value):
        # use Q to filter on user_permissions or group_permissions
        return queryset.filter(Q(user_permissions__id=value) | Q(groups__permissions__id=value))

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
            if model == "perm":
                queryset = self._filter_permissions(queryset, value)

        return queryset
