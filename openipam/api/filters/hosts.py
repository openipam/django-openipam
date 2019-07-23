from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError

from openipam.hosts.models import Host

from django_filters import FilterSet, CharFilter, NumberFilter

import re

from itertools import zip_longest

User = get_user_model()


class DisabledFlagFilter(NumberFilter):
    def filter(self, qs, value):
        if value == 1:
            qs = qs.extra(where=["hosts.mac IN (SELECT mac from disabled)"])
        elif value == 0:
            qs = qs.extra(where=["hosts.mac NOT IN (SELECT mac from disabled)"])
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


class UserWithGroupsFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            user = User.objects.filter(username__iexact=value).first()
            if user:
                qs = qs.by_owner(user=user, use_groups=True)
            else:
                qs = qs.none()
        return qs


class GroupFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            if "|" in value:
                groups = Group.objects.filter(name__in=value.split("|"))
                if groups:
                    qs = qs.by_groups(groups)
                else:
                    qs = qs.none()
            else:
                group = Group.objects.filter(name=value).first()
                if group:
                    qs = qs.by_group(group)
                else:
                    qs = qs.none()
        return qs


class AttributeFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            attribute_name = value.split(":")[0]
            if len(value.split(":")) == 2:
                attribute_value = value.split(":")[1]
            else:
                attribute_value = None

            if attribute_name and attribute_value:
                qs = qs.filter(
                    Q(
                        freeform_attributes__attribute__name=attribute_name,
                        freeform_attributes__value=attribute_value,
                    )
                    | Q(
                        structured_attributes__structured_attribute_value__attribute__name=attribute_name,
                        structured_attributes__structured_attribute_value__value=attribute_value,
                    )
                )
        return qs


class IPFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            try:
                qs = qs.filter(
                    Q(addresses__address=value) | Q(leases__address__address=value)
                ).distinct()
            except ValidationError:
                qs = qs.none()
        return qs


class HostCharFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            rgx = re.compile("[:,-. ]")
            mac_str = rgx.sub("", value)
            # Split to list to put back togethor with :
            mac_str = iter(mac_str)
            mac_str = ":".join(
                a + b for a, b in zip_longest(mac_str, mac_str, fillvalue="")
            )
            qs = qs.filter(mac__startswith=mac_str.lower())
        return qs


class NetworkFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            qs = qs.filter(addresses__network=value)
        return qs


# class HostDateTimeFilter(DateTimeFilter):
#     pass


class HostFilter(FilterSet):
    mac = HostCharFilter()
    hostname = CharFilter(lookup_expr="icontains")
    is_expired = IsExpiredFilter()
    group = GroupFilter()
    user = UserFilter()
    user_with_groups = UserWithGroupsFilter()
    ip_address = IPFilter()
    attribute = AttributeFilter()
    disabled = DisabledFlagFilter()
    network = NetworkFilter()
    # time = HostDateTimeFilter()

    class Meta:
        model = Host
        # TODO: This is dumb, django-filter 0.14 needs docs and bug fixes
        fields = ["hostname"]
