from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.core import serializers

from openipam.user.forms import GroupForm
from openipam.user.utils.user_utils import populate_user_from_ldap


def action_assign_groups(request, selected_users):
    user = request.user

    # User must have global change permission on hosts to use this action.
    if not user.has_perm("user.change_user"):
        messages.error(
            request,
            "You do not have permissions to change the selected users. "
            "Please contact an IPAM administrator.",
        )
    else:
        group_form = GroupForm(request.POST)

        if group_form.is_valid():
            groups = group_form.cleaned_data["groups"]

            for user in selected_users:
                for group in groups:
                    user.groups.add(group)

                data = [selected_users, groups]

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(user).pk,
                    object_id=user.pk,
                    object_repr=force_unicode(user),
                    action_flag=CHANGE,
                    change_message="Groups assigned to users: \n\n %s" % data,
                )

            messages.success(request, "Groups for selected users has been added.")

        else:
            error_list = []
            for key, errors in group_form.errors.items():
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error updating the groups of the selected users. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def action_remove_groups(request, selected_users):
    user = request.user

    # User must have global change permission on hosts to use this action.
    if not user.has_perm("user.change_user"):
        messages.error(
            request,
            "You do not have permissions to change the selected users. "
            "Please contact an IPAM administrator.",
        )
    else:
        group_form = GroupForm(request.POST)

        if group_form.is_valid():
            groups = group_form.cleaned_data["groups"]

            for group in groups:
                for user in selected_users:
                    group.user_set.remove(user)

                data = [selected_users, groups]

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(user).pk,
                    object_id=user.pk,
                    object_repr=force_unicode(user),
                    action_flag=CHANGE,
                    change_message="Groups removed from users: \n\n %s" % data,
                )

            messages.success(request, "Groups for selected users has been removed.")

        else:
            error_list = []
            for key, errors in group_form.errors.items():
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error updating the groups of the selected users. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def action_assign_perms(request, selected_users):
    user = request.user

    # User must have global change permission on hosts to use this action.
    if not user.has_perm("user.change_user"):
        messages.error(
            request,
            "You do not have permissions to change the selected users. "
            "Please contact an IPAM administrator.",
        )
    else:
        group_form = GroupForm(request.POST)

        if group_form.is_valid():
            groups = group_form.cleaned_data["groups"]

            for group in groups:
                for user in selected_users:
                    group.user_set.remove(user)

                data = [selected_users, groups]

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(user).pk,
                    object_id=user.pk,
                    object_repr=force_unicode(user),
                    action_flag=CHANGE,
                    change_message="Groups removed from users: \n\n %s" % data,
                )

            messages.success(request, "Groups for selected users has been removed.")

        else:
            error_list = []
            for key, errors in group_form.errors.items():
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error updating the groups of the selected users. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def action_populate_user(request, selected_users):
    user = request.user

    # User must have global change permission on hosts to use this action.
    if not user.has_perm("user.change_user"):
        messages.error(
            request,
            "You do not have permissions to change the selected users. "
            "Please contact an IPAM administrator.",
        )
    else:
        for user in selected_users:
            populate_user_from_ldap(user=user)

        messages.success(request, "Selected users have been populated from LDAP.")
