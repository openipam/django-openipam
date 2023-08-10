from rest_framework import permissions
from openipam.dns.models import Domain

from openipam.hosts.models import Host
from guardian.shortcuts import get_objects_for_user
from django.db.models.functions import Length


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


class DnsRecordPermissions(permissions.DjangoModelPermissions):
    """Permission to delete a DNS record."""

    def has_permission(self, request, view):
        # For post requests, we need to make sure the user is allowed to add
        # records of the given type
        if request.method == "POST":
            # Get the record type from the request
            record_type = request.data.get("dns_type", None)
            if not record_type:
                return False
            # This isn't implemented properly, so we have to hardcode the
            # record types that are allowed to be added by non-admins
            allowed_types = [
                "A",
                "CNAME",
                "HINFO",
                "MX",
                "NS",
                "TXT",
                "PTR",
                "SRV",
                "SSHFP",
            ]
            if request.user.is_ipamadmin:
                return True
            if record_type not in allowed_types:
                return False
            # Now, check that the user has permission to add records to the domain
            name = request.data.get("name", None)
            if not name:
                return False
            # Need the domain whose name is the end of the record name
            name_segments = name.split(".")
            domain_name_possibilities = [
                ".".join(name_segments[i:]) for i in range(len(name_segments))
            ]
            # Get the longest domain name that this record could be a part of
            domain = (
                Domain.objects.filter(name__in=domain_name_possibilities)
                .order_by(Length("name").desc())
                .first()
            )
            if not domain:
                return False
            # Check if the user has permission to add records to this domain
            if request.user.has_perm(
                "dns.is_owner_domain",
                domain,
            ) or request.user.has_perm(
                "dns.add_records_to_domain",
                domain,
            ):
                return True
            # Otherwise, return false
            return False
        # If not delete, return the default permission
        if request.method != "DELETE":
            return super(DnsRecordPermissions, self).has_permission(request, view)
        # Delete requests are left up to the object-level permissions.
        return True

    def has_object_permission(self, request, view, obj):
        # Return true for non-delete requests
        if request.method != "DELETE":
            return True

        # Allow deletion if the user is an admin
        if request.user.is_ipamadmin:
            return True

        # Allow deletion if the user owns the domain
        if request.user.has_perm("dns.is_owner_domain", obj.domain):
            return True

        # Allow deletion if the user owns the associated host
        if request.user.has_perm("hosts.is_owner_host", obj.host):
            return True

        # Deny deletion
        return False
