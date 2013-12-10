from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs
from django.utils.functional import wraps
from openipam.hosts.models import Host
#require_http_methods


def permission_owner_required(view_func):
    """
    Decorator for views that checks that the User has owner permission
    on a host.
    """

    #@wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, pk, *args, **kwargs):

        permited_host = Host.objects.get_host_with_owner_perms(request.user, pk=pk)
        if permited_host:
            return view_func(request, *args, **kwargs)
        else:
            from openipam.hosts.views import HostDetailView

            host_view = HostDetailView.as_view()
            response = host_view(request, pk=pk, read_only=True, *args, **kwargs)
            return response.render()

    return wraps(view_func)(_wrapped_view)
