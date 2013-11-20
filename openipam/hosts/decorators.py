from django.core.exceptions import PermissionDenied

from openipam.hosts.models import Host


def permission_owner_required(view_func):
    """
    Decorator for views that checks that the User has owner permission
    on a host.
    """
    def wrap(request, pk, *args, **kwargs):

        permited_host = Host.objects.get_hosts_with_owner_perms(request.user, pk=pk)

        if permited_host:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap

