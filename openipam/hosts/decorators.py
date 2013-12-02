from django.core.exceptions import PermissionDenied
from openipam.hosts.models import Host


def permission_owner_required(view_func):
    """
    Decorator for views that checks that the User has owner permission
    on a host.
    """
    def wrap(request, pk, *args, **kwargs):

        permited_host = Host.objects.get_host_with_owner_perms(request.user, pk=pk)

        if not permited_host:
            from openipam.hosts.views import HostDetailView

            view_func = HostDetailView.as_view()
            response = view_func(request, pk=pk, read_only=True, *args, **kwargs)
            return response.render()

    return wrap

