from rest_framework import permissions

from openipam.hosts.models import Host
from guardian.shortcuts import get_objects_for_user


class APIAdminPermission(permissions.BasePermission):
    """Global permission check for Admin users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_ipamadmin


class ChangeHostPermission(permissions.BasePermission):
    """Permission to change a given host."""

    def has_permission(self, request, view):
        """Check if user has permission to change host."""
        if request.user.is_ipamadmin:
            return True
        pk = view.kwargs.get("pk", None)
        permitted_host = Host.objects.by_change_perms(request.user, pk=pk)
        return permitted_host.exists()


class HasGlobalPermission(permissions.BasePermission):
    """Generic class to check if user has a global permission."""

    permission = None

    def __init__(self, permission, *args, **kwargs):
        super(HasGlobalPermission, self).__init__(*args, **kwargs)
        self.permission = permission

    @classmethod
    def perm(cls, permission):
        """
        Return a subclass of HasGlobalPermission with the permission set.

        Useful for using in the permission_classes attribute of a view or
        viewset.
        """
        subclass = type("HasGlobalPermission", (cls,), {})
        # create an init method for the subclass
        subclass.__init__ = lambda self, *args, **kwargs: super(
            subclass, self
        ).__init__(permission, *args, **kwargs)
        return subclass

    def has_permission(self, request, view, obj):
        """Check if user has permission."""
        return request.user.is_ipamadmin or request.user.has_perm(self.permission)


class HasObjectPermission(HasGlobalPermission):
    """
    Generic class to check if a user has an object-level permission.

    Succeeds if the user has the listed permission, or is an administrator.
    """

    model = None

    def __init__(self, permission, model, *args, **kwargs):
        super(HasObjectPermission, self).__init__(permission, *args, **kwargs)
        self.model = model

    @classmethod
    def perm(cls, permission, model):
        """
        Return a subclass of HasObjectPermission with the permission set.

        Useful for using in the permission_classes attribute of a view or
        viewset.
        """
        subclass = type("HasObjectPermission", (cls,), {})
        # create an init method for the subclass
        subclass.__init__ = lambda self, *args, **kwargs: super(
            subclass, self
        ).__init__(permission, model, *args, **kwargs)
        return subclass

    def has_permission(self, request, view):
        """As this permission only checks object-level permissions, always return True."""
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user has permission."""
        if request.user.is_ipamadmin:
            return True
        if not obj:
            return False
        if not isinstance(obj, self.model):
            return False

        user_perms = get_objects_for_user(
            request.user, [self.permission], self.model.objects.filter(pk=obj.pk)
        )
        return user_perms.exists()


class HostPermission(permissions.BasePermission):
    """Permission to access a given host."""

    def has_permission(self, request, view):
        """Check if user has permission to access hosts."""
        if not request.user.is_authenticated:
            return False  # Only authenticated users can access hosts
        if request.method == "POST":
            return request.user.has_perm(
                "hosts.add_host"
            )  # Check for global permission to add hosts
        return True  # Default allow access to hosts. Object-level permissions will be checked later

    def has_object_permission(self, request, view, obj, check_for_read=False):
        """Check if user has permission to access host."""
        if request.user.is_ipamadmin:
            return True
        if request.method in permissions.SAFE_METHODS and not check_for_read:
            return True  # Anyone can view any host
        if not obj:
            return False  # No object, no permission
        if not isinstance(obj, Host):
            print("WARNING: Object is not a host, this was probably a mistake")
            return False  # Object is not a host, this was probably a mistake
        permitted_host = Host.objects.by_change_perms(request.user, pk=obj.pk)
        if permitted_host:
            return True
        return False  # Default deny access to host


class ReadRestrictObjectPermissions(permissions.DjangoObjectPermissions):
    """Model permission that also restricts read access to objects."""

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }
