from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from openipam.hosts.models import Host

from rest_framework import filters

from guardian.shortcuts import get_objects_for_group, get_objects_for_user

User = get_user_model()


class HostGroupFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        groupname = request.GET.get("group", "")
        if groupname:
            group = Group.objects.filter(name=groupname).first()
            if group:
                group_hosts = get_objects_for_group(
                    group, ["hosts.is_owner_host"], klass=Host
                )
                return queryset.filter(pk__in=[host.pk for host in group_hosts])
            else:
                return queryset.none()
        else:
            return queryset


class HostOwnerFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        owner = request.GET.get("owner", "")
        use_groups = request.GET.get("use_groups", "")
        if owner:
            user = User.objects.filter(username__iexact=owner).first()
            if user:
                user_hosts = get_objects_for_user(
                    user,
                    ["hosts.is_owner_host"],
                    klass=Host,
                    use_groups=True if use_groups else False,
                    with_superuser=False,
                )
                return queryset.filter(pk__in=[host.pk for host in user_hosts])
            else:
                return queryset.none()
        else:
            return queryset
