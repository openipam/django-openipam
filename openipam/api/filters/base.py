from django.contrib.auth import get_user_model

from django_filters import FilterSet, CharFilter, NumberFilter

from guardian.shortcuts import get_objects_for_user

User = get_user_model()


class UsernameFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            user = User.objects.filter(username__iexact=value).first()
            if user:
                user_hosts = get_objects_for_user(
                    user,
                    ['hosts.is_owner_host'],
                    with_superuser=False
                )
                qs = qs.filter(pk__in=[host.pk for host in user_hosts])
            else:
                qs = qs.none()
        return qs
