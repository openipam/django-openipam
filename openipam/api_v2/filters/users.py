# import Concat from django
from rest_framework import filters
import django_filters as df
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user
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
