from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models import Q

from openipam.hosts.models import Host

from guardian.shortcuts import get_objects_for_group, get_objects_for_user

from django_filters import FilterSet, CharFilter, NumberFilter

from netaddr import AddrFormatError

User = get_user_model()


class DisabledFlagFilter(NumberFilter):
    def filter(self, qs, value):
        if value == 1:
            qs = qs.filter(disabled_host__isnull=False)
        elif value == 0:
            qs = qs.filter(disabled_host__isnull=True)
        return qs


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
            user = User.objects.filter(username__iexact=value).first()
            if user:
                qs = qs.by_owner(user)
            else:
                qs = qs.none()
        return qs


class GroupFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            group = Group.objects.filter(name=value).first()
            if group:
                qs = qs.by_group(group)
            else:
                qs = qs.none()
        return qs


class AttributeFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            attribute_name = value.split(':')[0]
            if len(value.split(':')) == 2:
                attribute_value = value.split(':')[1]
            else:
                attribute_value = None

            if attribute_name and attribute_value:
                qs = qs.filter(
                    Q(freeform_attributes__attribute__name=attribute_name, freeform_attributes__value=attribute_value) |
                    Q(
                        structured_attributes__structured_attribute_value__attribute__name=attribute_name,
                        structured_attributes__structured_attribute_value__value=attribute_value
                    )
                )
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
    attribute = AttributeFilter()
    disabled = DisabledFlagFilter()

    class Meta:
        model = Host
        fields = ['mac', 'hostname']
