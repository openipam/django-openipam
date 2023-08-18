# import Concat from django
from rest_framework import filters
import django_filters as df
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user
from django.db.models import functions as dfn

User = get_user_model()


class UserFilterSet(df.FilterSet):
    """Filterset for users."""

    username = df.CharFilter(lookup_expr="icontains")
    full_name = df.CharFilter(method="filter_full_name", label="Full Name")
    email = df.CharFilter(lookup_expr="icontains")
    groups = df.CharFilter(method="filter_groups", label="Groups")
    is_active = df.BooleanFilter()
    is_staff = df.BooleanFilter()
    is_superuser = df.BooleanFilter()
    is_ipamadmin = df.BooleanFilter()

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
