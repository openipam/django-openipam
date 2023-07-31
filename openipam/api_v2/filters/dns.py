"""Filters for dns records."""
from django.db.models import Q
from rest_framework import filters
from openipam.dns.models import Domain, DnsRecord
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user
from django_filters import FilterSet, CharFilter
User = get_user_model()


class ContentFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            try:
                qs = qs.filter(
                    Q(ip_content__address__icontains=value)
                    | Q(text_content__icontains=value)
                ).distinct()
            except ValidationError:
                qs = qs.none()
        return qs


class TypeFilter(filters.SearchFilter):
    def filter(self, qs, value):
        if value:
            qs = qs.filter(dns_type__name__iexact=value)
        return qs


class DnsFilter(FilterSet):
    """Filter for dns records."""
    name = CharFilter(lookup_expr="icontains")
    text_content = ContentFilter()
    ip_content = ContentFilter()
    type = TypeFilter()

    class Meta:
        model = DnsRecord
        fields = ["name", "text_content", "ip_content", "dns_type"]


class UserFilter(filters.SearchFilter):
    def filter(self, qs, value):
        if value:
            user = User.objects.filter(username__iexact=value)
            if user:
                user = user[0]
                if user.is_ipamadmin:
                    return qs
                else:
                    user_domains = get_objects_for_user(
                        user,
                        [
                            "dns.add_records_to_domain",
                            "dns.is_owner_domain",
                            "dns.change_domain",
                        ],
                        klass=Domain,
                        any_perm=True,
                    )

                    qs = qs.filter(pk__in=[domain.pk for domain in user_domains])
            else:
                qs = qs.none()
        return qs


class DomainFilter(FilterSet):
    name = filters.SearchFilter()
    username = UserFilter()

    class Meta:
        model = Domain
        fields = ["name"]
