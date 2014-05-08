from django.contrib.auth import get_user_model

from openipam.dns.models import Domain

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
    name = CharFilter(lookup_type='icontains')
    username = UserFilter()

    class Meta:
        model = Domain
        fields = ['name']

