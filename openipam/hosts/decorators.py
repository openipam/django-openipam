from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs
from django.utils.functional import wraps
from openipam.hosts.models import Host
#require_http_methods


def permission_owner_host(view_func):
    """
    Decorator for views that checks that the User has owner permission
    on a host.
    """
    def _wrapped_view(request, pk, *args, **kwargs):
        permited_host = Host.objects.by_change_perms(request.user, pk=pk)
        if permited_host:
            return view_func(request, *args, **kwargs)
        else:
            from openipam.hosts.views import HostDetailView

            host_view = HostDetailView.as_view()
            response = host_view(request, pk=pk, read_only=True, *args, **kwargs)
            return response.render()
    return wraps(view_func)(_wrapped_view)


def permission_view_host(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.has_perm('hosts.view_host'):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wraps(view_func)(_wrapped_view)


def permission_add_host(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.has_perm('hosts.add_host'):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wraps(view_func)(_wrapped_view)
