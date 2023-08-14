"""Filters for dns records."""
from django.db.models import Q
from rest_framework import filters
from openipam.dns.models import DhcpDnsRecord, DnsType, Domain, DnsRecord
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user
from django_filters import FilterSet, CharFilter

User = get_user_model()


class ContentFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            try:
                qs = qs.filter(Q(ip_content__address__icontains=value) | Q(text_content__icontains=value)).distinct()
            except ValidationError:
                qs = qs.none()
        return qs


class DnsFilter(FilterSet):
    """Filter for dns records."""

    name = CharFilter(method="filter_name", label="Name")
    content = CharFilter(method="filter_content", label="Content")
    dns_type = CharFilter(method="filter_dns_type", label="DNS Type")

    class Meta:
        model = DnsRecord
        fields = ["name", "content", "dns_type"]

    def filter_content(self, queryset, _, value):
        """Filter based on content."""
        print(value)
        if value:
            try:
                queryset = queryset.filter(
                    Q(ip_content__address__istartswith=value) | Q(text_content__icontains=value)
                ).distinct()
            except ValidationError:
                queryset = queryset.none()
        return queryset

    def filter_name(self, queryset, _, value):
        """Filter based on name."""
        if value:
            queryset = queryset.filter(name__istartswith=value)
        return queryset

    def filter_dns_type(self, queryset, _, value):
        """Filter based on dns_type."""
        if value:
            queryset = queryset.filter(dns_type__name__istartswith=value)
        return queryset


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
    """Filter for domains."""

    name = CharFilter(method="filter_name", label="Name")
    changed_by = CharFilter(method="filter_changed_by", label="Changed By")

    def filter_changed_by(self, queryset, _, value):
        """Filter based on changed_by."""
        if value:
            queryset = queryset.filter(changed_by__username__iexact=value)
        return queryset

    def filter_name(self, queryset, _, value):
        """Filter based on name."""
        if value:
            queryset = queryset.filter(name__istartswith=value)
        return queryset

    class Meta:
        model = Domain
        fields = ["name", "changed_by"]


class DhcpDnsFilter(FilterSet):
    """Filter for DHCP DNS records."""

    host = CharFilter(method="filter_host", label="Host")
    mac = CharFilter(method="filter_mac", label="MAC")
    ip_address = CharFilter(method="filter_ip_address", label="IP Address")
    domain = CharFilter(method="filter_domain", label="Domain")

    def filter_host(self, queryset, _, value):
        """Filter based on host."""
        if value:
            queryset = queryset.filter(host__hostname__istartswith=value)
        return queryset

    def filter_domain(self, queryset, _, value):
        """Filter based on domain."""
        if value:
            queryset = queryset.filter(domain__name__istartswith=value)
        return queryset

    def filter_mac(self, queryset, _, value):
        """Filter based on mac."""
        if value:
            queryset = queryset.filter(host__mac__istartswith=value)
        return queryset

    def filter_ip_address(self, queryset, _, value):
        """Filter based on ip_address."""
        if value:
            queryset = queryset.filter(ip_content__address__istartswith=value)
        return queryset

    class Meta:
        model = DhcpDnsRecord
        fields = ["host", "ip_address", "domain", "mac"]


class DnsTypeFilter(FilterSet):
    """Filter for DNS types."""

    name = CharFilter(lookup_expr="icontains")
    description = CharFilter(lookup_expr="icontains")

    class Meta:
        model = DnsType
        fields = ["name", "description"]
