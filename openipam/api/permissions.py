from rest_framework import permissions

from openipam.conf.ipam_settings import CONFIG


class IPAMAPIAdminPermission(permissions.BasePermission):
    '''
    Permission against users who need to be in the ipam-api group
    '''

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        has_api_group = request.user.groups.filter(name=CONFIG.get('API_ADMIN_GROUP'))
        if has_api_group:
            return True

        return False


class IPAMAPIPermission(permissions.BasePermission):
    '''
    Permission against users who need to be in the ipam-api group
    '''

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        has_api_group = request.user.groups.filter(name=CONFIG.get('API_USER_GROUP'))
        if has_api_group:
            return True

        return False
