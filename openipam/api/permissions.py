from rest_framework import permissions

from openipam.conf.ipam_settings import CONFIG
from openipam.hosts.models import Host

from guardian.shortcuts import get_objects_for_user


class IPAMAPIAdminPermission(permissions.BasePermission):
    """
    Permission against users who need to be in the ipam-api group
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        has_api_group = request.user.groups.filter(name=CONFIG.get("API_ADMIN_GROUP"))
        if has_api_group:
            return True

        return False


class IPAMAPIPermission(permissions.BasePermission):
    """
    Permission against users who need to be in the ipam-api group
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        has_api_group = request.user.groups.filter(name=CONFIG.get("API_USER_GROUP"))
        if has_api_group:
            return True

        return False


class IPAMChangeHostPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        pk = view.kwargs.get("pk", None)
        permited_host = Host.objects.by_change_perms(request.user, pk=pk)
        return True if permited_host else False


class IPAMGuestEnablePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        guests_enabled = CONFIG.get("GUESTS_ENABLED", False)
        return guests_enabled
