from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models import Q

from openipam.hosts.models import Host

from guardian.shortcuts import get_objects_for_group, get_objects_for_user

from django_filters import FilterSet, CharFilter, NumberFilter

from netaddr import AddrFormatError

User = get_user_model()


class IsExpiredFilter(NumberFilter):
    def filter(self, qs, value):
        if value == 1:
            qs = qs.filter(expires__lt=timezone.now())
        elif value == 0:
            qs = qs.filter(expires__gte=timezone.now())
        return qs


class UserFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            user = User.objects.filter(username__iexact=value)
            if user:
                user[0].is_superuser = False
                user_hosts = get_objects_for_user(
                    user[0],
                    ['hosts.is_owner_host'],
                    klass=Host,
                )
                qs = qs.filter(pk__in=[host.pk for host in user_hosts])
            else:
                qs = qs.none()
        return qs


class GroupFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            group = Group.objects.filter(name=value)
            if group:
                group_hosts = get_objects_for_group(
                    group[0],
                    ['hosts.is_owner_host'],
                    klass=Host,
                )
                qs = qs.filter(pk__in=[host.pk for host in group_hosts])
            else:
                qs = qs.none()
        return qs


class IPFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            try:
                qs = qs.filter(Q(addresses__address=value) | Q(leases__address__address=value)).distinct()
            except AddrFormatError:
                qs = qs.none()
        return qs


class HostFilter(FilterSet):
    mac = CharFilter(lookup_type='istartswith')
    hostname = CharFilter(lookup_type='icontains')
    is_expired = IsExpiredFilter()
    group = GroupFilter()
    user = UserFilter()
    ip_address = IPFilter()

    class Meta:
        model = Host
        fields = ['mac', 'hostname']


