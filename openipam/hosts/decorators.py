from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs
from django.utils.functional import wraps
from openipam.hosts.models import Host


def permission_change_host(view_func):
    """
    Decorator for views that checks that the User has owner permission
    on a host.
    """
    def _wrapped_view(request, pk, *args, **kwargs):
        permited_host = Host.objects.by_change_perms(request.user, pk=pk)
        if permited_host and not permited_host.is_disabled:
            return view_func(request, *args, **kwargs)
        else:
            from openipam.hosts.views import HostDetailView

            host_view = HostDetailView.as_view()
            response = host_view(request, pk=pk, read_only=True, *args, **kwargs)
            return response
    return wraps(view_func)(_wrapped_view)
# TODO:  Temp function until perms changes.
permission_owner_required = permission_change_host
