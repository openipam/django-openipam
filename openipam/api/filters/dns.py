from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError

from openipam.dns.models import Domain, DnsRecord

from django_filters import FilterSet, CharFilter

from guardian.shortcuts import get_objects_for_user

User = get_user_model()


class UserFilter(CharFilter):
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
                        ['dns.add_records_to_domain', 'dns.is_owner_domain', 'dns.change_domain'],
                        klass=Domain,
                        any_perm=True
                    )

                    qs = qs.filter(pk__in=[domain.pk for domain in user_domains])
            else:
                qs = qs.none()
        return qs


class DomainFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')
    username = UserFilter()

    class Meta:
        model = Domain
        fields = ['name']


class ContentFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            try:
                qs = qs.filter(Q(ip_content__address__icontains=value) | Q(text_content__icontains=value)).distinct()
            except ValidationError:
                qs = qs.none()
        return qs


class TypeFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            qs = qs.filter(dns_type__name__iexact=value)
        return qs


class DnsFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')
    content = ContentFilter()
    type = TypeFilter()

    class Meta:
        model = DnsRecord
        fields = ['name', 'content', 'dns_type']
