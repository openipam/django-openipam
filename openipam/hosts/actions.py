from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.core import serializers

from openipam.hosts.models import Host
from openipam.hosts.forms import HostOwnerForm, HostRenewForm


def assign_owner_hosts(request, selected_hosts, add_only=False):
    user = request.user

    # User must have global change permission on hosts to use this action.
    if not user.has_perm('hosts.change_host'):
        messages.error(request, "You do not have permissions to change ownership on the selected hosts. "
                       "Please contact an IPAM administrator.")
    else:
        owner_form = HostOwnerForm(request.POST)

        if owner_form.is_valid():
            user_owners = owner_form.cleaned_data['user_owners']
            group_owners = owner_form.cleaned_data['group_owners']

            for host in selected_hosts:
                # Delete user and group permissions first
                if not add_only:
                    host.remove_owners()

                # Re-assign users
                for user_onwer in user_owners:
                    host.assign_owner(user_onwer)

                # Re-assign groups
                for group_owner in group_owners:
                    host.assign_owner(group_owner)

            messages.success(request, "Ownership for selected hosts has been updated.")

        else:
            error_list = []
            for key, errors in owner_form.errors.items():
                for error in errors:
                    error_list.append(error)
            messages.error(request, mark_safe("There was an error updating the ownership of the selected hosts. "
                    "<br/>%s" % '<br />'.join(error_list)))


def remove_owner_hosts(request, selected_hosts):
    user = request.user

    # User must have global change permission on hosts to use this action.
    if not user.has_perm('hosts.change_host'):
        messages.error(request, "You do not have permissions to change ownership on the selected hosts. "
                       "Please contact an IPAM administrator.")
    else:
        owner_form = HostOwnerForm(request.POST)

        if owner_form.is_valid():
            user_owners = owner_form.cleaned_data['user_owners']
            group_owners = owner_form.cleaned_data['group_owners']

            for host in selected_hosts:
                # Re-assign users
                for user_onwer in user_owners:
                    host.remove_owner(user_onwer)

                # Re-assign groups
                for group_owner in group_owners:
                    host.remove_owner(group_owner)

            messages.success(request, "Ownership for selected hosts has been updated.")

        else:
            error_list = []
            for key, errors in owner_form.errors.items():
                for error in errors:
                    error_list.append(error)
            messages.error(request, mark_safe("There was an error updating the ownership of the selected hosts. "
                    "<br/>%s" % '<br />'.join(error_list)))


def delete_hosts(request, selected_hosts):
    user = request.user

    # Must have global delete perm or object owner perm
    if not user.has_perm('hosts.delete_host') and not change_perms_check(user, selected_hosts):
        messages.error(request, "You do not have permissions to perform this action on one or more the selected hosts. "
                       "Please contact an IPAM administrator.")
    else:
        # Log Deletion
        for host in selected_hosts:
            data = serializers.serialize('json', [host])

            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=force_unicode(host),
                action_flag=DELETION,
                change_message=data
            )

        # Delete hosts
        selected_hosts.delete_and_free(user=request.user)

        messages.success(request, "Seleted hosts have been deleted.")


def renew_hosts(request, selected_hosts):
    user = request.user

    # Must have global delete perm or object owner perm
    if not user.has_perm('hosts.change_host') and not change_perms_check(user, selected_hosts):
        messages.error(request, "You do not have permissions to perform this action one or more of the selected hosts. "
                       "Please contact an IPAM administrator.")
    else:
        renew_form = HostRenewForm(user=request.user, data=request.POST)

        if renew_form.is_valid():
            expiration = renew_form.cleaned_data['expire_days'].expiration
            for host in selected_hosts:
                data = serializers.serialize('json', [host])

                host.set_expiration(expiration)
                host.save()

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(host).pk,
                    object_id=host.pk,
                    object_repr=force_unicode(host),
                    action_flag=CHANGE,
                    change_message=data
                )

            messages.success(request, "Expiration for selected hosts have been updated.")

        else:
            error_list = []
            for key, errors in renew_form.errors.items():
                for error in errors:
                    error_list.append(error)
            messages.error(request, mark_safe("There was an error renewing the expiration of the selected hosts. "
                    "<br/>%s" % '<br />'.join(error_list)))


def change_addresses(request, selected_hosts):
    pass



def change_perms_check(user, selected_hosts):
    # Check onwership of hosts for users with only object level permissions.
    host_perms_qs = Host.objects.filter(mac__in=[host.mac for host in selected_hosts]).by_change_perms(user)
    for host in selected_hosts:
        if host not in host_perms_qs:
            return False
    return True
