from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Q

from openipam.hosts.models import (
    Host,
    Disabled,
    StructuredAttributeToHost,
    FreeformAttributeToHost,
    GulRecentArpByaddress,
    GulRecentArpBymac,
)
from openipam.hosts.forms import (
    HostOwnerForm,
    HostRenewForm,
    HostAttributesCreateForm,
    HostAttributesDeleteForm,
    HostRenameForm,
    HostDhcpGroupForm,
)

import csv
import re

User = get_user_model()


def assign_owner_hosts(request, selected_hosts, add_only=False):
    user = request.user

    # User must have global change perm or object owner perm.
    if not user.has_perm("hosts.change_host") and not change_perms_check(
        user, selected_hosts
    ):
        messages.error(
            request,
            "You do not have permissions to perform this action on one or more the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        owner_form = HostOwnerForm(request.POST)

        if owner_form.is_valid():
            user_owners = owner_form.cleaned_data["user_owners"]
            group_owners = owner_form.cleaned_data["group_owners"]

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

                data = [user_owners, group_owners]

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(host).pk,
                    object_id=host.pk,
                    object_repr=force_text(host),
                    action_flag=CHANGE,
                    change_message="Owners assigned to host: \n\n %s" % data,
                )

            messages.success(request, "Ownership for selected hosts has been updated.")

        else:
            error_list = []
            for key, errors in list(owner_form.errors.items()):
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error updating the ownership of the selected hosts. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def remove_owner_hosts(request, selected_hosts):
    user = request.user

    # User must have global change perm or object owner perm.
    if not user.has_perm("hosts.change_host") and not change_perms_check(
        user, selected_hosts
    ):
        messages.error(
            request,
            "You do not have permissions to perform this action on one or more the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        owner_form = HostOwnerForm(request.POST)

        if owner_form.is_valid():
            user_owners = owner_form.cleaned_data["user_owners"]
            group_owners = owner_form.cleaned_data["group_owners"]

            for host in selected_hosts:
                # Re-assign users
                for user_onwer in user_owners:
                    host.remove_owner(user_onwer)

                # Re-assign groups
                for group_owner in group_owners:
                    host.remove_owner(group_owner)

                data = [user_owners, group_owners]

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(host).pk,
                    object_id=host.pk,
                    object_repr=force_text(host),
                    action_flag=CHANGE,
                    change_message="Owners removed from host: \n\n %s" % data,
                )

            messages.success(request, "Ownership for selected hosts has been updated.")

        else:
            error_list = []
            for key, errors in list(owner_form.errors.items()):
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error updating the ownership of the selected hosts. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def delete_hosts(request, selected_hosts):
    user = request.user

    # Must have global delete perm or object owner perm
    if not user.has_perm("hosts.delete_host") and not change_perms_check(
        user, selected_hosts
    ):
        messages.error(
            request,
            "You do not have permissions to perform this action on one or more the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        # Log Deletion
        for host in selected_hosts:
            data = serializers.serialize("json", [host])

            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=force_text(host),
                action_flag=DELETION,
                change_message=data,
            )

        # Delete hosts
        selected_hosts.delete(user=request.user)

        messages.success(request, "Selected hosts have been deleted.")


def renew_hosts(request, selected_hosts):
    user = request.user

    # Must have global delete perm or object owner perm
    if not user.has_perm("hosts.change_host") and not change_perms_check(
        user, selected_hosts
    ):
        messages.error(
            request,
            "You do not have permissions to perform this action one or more of the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        renew_form = HostRenewForm(user=request.user, data=request.POST)

        if renew_form.is_valid():
            expiration = renew_form.cleaned_data["expire_days"].expiration
            for host in selected_hosts:
                data = serializers.serialize("json", [host])

                host.set_expiration(expiration)
                host.save(user=user)

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(host).pk,
                    object_id=host.pk,
                    object_repr=force_text(host),
                    action_flag=CHANGE,
                    change_message=data,
                )

            messages.success(
                request, "Expiration for selected hosts have been updated."
            )

        else:
            error_list = []
            for key, errors in list(renew_form.errors.items()):
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error renewing the expiration of the selected hosts. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def rename_hosts(request, selected_hosts):
    user = request.user

    # Must super user access (for now)
    if not user.is_superuser:
        messages.error(
            request,
            "You do not have permissions to perform this action one or more of the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        rename_form = HostRenameForm(data=request.POST)

        if rename_form.is_valid():
            regex = rename_form.cleaned_data["regex"]
            substitution = rename_form.cleaned_data["substitution"]

            for host in selected_hosts:
                current_hostname = host.hostname
                new_hostname = re.sub(regex, substitution, current_hostname)
                host.set_hostname(hostname=new_hostname, user=user)
                host.save(user=user)

            messages.success(request, "Renaming for selected hosts have been applied.")

        else:
            error_list = []
            for key, errors in list(rename_form.errors.items()):
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error renaming the selected hosts. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def change_addresses(request, selected_hosts):
    pass


def add_attribute_to_hosts(request, selected_hosts):
    user = request.user
    attribute_form = HostAttributesCreateForm(data=request.POST)

    # Must have global change perm or object owner perm
    if not user.has_perm("hosts.change_host") and not change_perms_check(
        user, selected_hosts
    ):
        messages.error(
            request,
            "You do not have permissions to perform this action one or more of the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        if attribute_form.is_valid():
            for host in selected_hosts:

                attribute = attribute_form.cleaned_data["add_attribute"]

                if attribute.structured:
                    StructuredAttributeToHost.objects.create(
                        host=host,
                        structured_attribute_value=attribute_form.cleaned_data[
                            "choice_value"
                        ],
                        changed_by=user,
                    )
                else:
                    FreeformAttributeToHost.objects.create(
                        host=host,
                        attribute=attribute,
                        value=attribute_form.cleaned_data["text_value"],
                        changed_by=user,
                    )

            messages.success(request, "Attributes for selected hosts have been added.")

        else:
            error_list = []
            for key, errors in list(attribute_form.errors.items()):
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error adding attributes to the selected hosts. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def delete_attribute_from_host(request, selected_hosts):
    user = request.user
    attribute_form = HostAttributesDeleteForm(data=request.POST)

    # Must have global change perm or object owner perm
    if not user.has_perm("hosts.change_host") and not change_perms_check(
        user, selected_hosts
    ):
        messages.error(
            request,
            "You do not have permissions to perform this action one or more of the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:

        if attribute_form.is_valid():
            for host in selected_hosts:

                attribute = attribute_form.cleaned_data["del_attribute"]

                if attribute.structured:
                    StructuredAttributeToHost.objects.filter(
                        host=host, structured_attribute_value__attribute=attribute
                    ).delete()
                else:
                    FreeformAttributeToHost.objects.filter(
                        host=host, attribute=attribute
                    ).delete()
            messages.success(
                request, "Attributes for selected hosts have been deleted."
            )


def set_dhcp_group_on_host(request, selected_hosts):
    user = request.user

    # Must super user access (for now)
    if not user.is_superuser:
        messages.error(
            request,
            "You do not have permissions to perform this action one or more of the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        dhcp_group_form = HostDhcpGroupForm(data=request.POST)

        if dhcp_group_form.is_valid():
            for host in selected_hosts:
                host.dhcp_group = dhcp_group_form.cleaned_data["dhcp_group"]
                host.save(user=user)

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(host).pk,
                    object_id=host.pk,
                    object_repr=force_text(host),
                    action_flag=CHANGE,
                    change_message="DHCP Group set.",
                )

            messages.success(request, "DHCP Groups for selected hosts have been set.")

        else:
            error_list = []
            for key, errors in list(dhcp_group_form.errors.items()):
                for error in errors:
                    error_list.append(error)
            messages.error(
                request,
                mark_safe(
                    "There was an error setting the DHCP group to the selected hosts. "
                    "<br/>%s" % "<br />".join(error_list)
                ),
            )


def delete_dhcp_group_on_host(request, selected_hosts):
    user = request.user

    # Must super user access (for now)
    if not user.is_superuser:
        messages.error(
            request,
            "You do not have permissions to perform this action one or more of the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        for host in selected_hosts:
            host.dhcp_group = None
            host.save(user=user)

            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=force_text(host),
                action_flag=CHANGE,
                change_message="DHCP Group deleted.",
            )

        messages.success(request, "DHCP Groups for selected hosts have been deleted.")


def populate_primary_dns(request, selected_hosts):
    user = request.user

    # Must have global delete perm or object owner perm
    if not user.has_perm("hosts.change_host") and not change_perms_check(
        user, selected_hosts
    ):
        messages.error(
            request,
            "You do not have permissions to perform this action on one or more the selected hosts. "
            "Please contact an IPAM administrator.",
        )
    else:
        # Log Deletion
        for host in selected_hosts:
            host.delete_dns_records(user=user)
            host.add_dns_records(user=user)

            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(host).pk,
                object_id=host.pk,
                object_repr=force_text(host),
                action_flag=CHANGE,
                change_message="Primary DNS Records populated.",
            )

        messages.success(request, "DNS for selected hosts have been populated.")


def export_csv(request, selected_hosts):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="hosts.csv"'
    writer = csv.writer(response)

    writer.writerow(
        [
            "Hostname",
            "Mac",
            "Expires",
            "IP Address",
            "Mac Last Seen",
            "IP Last Seen",
            "Users",
            "User Emails",
            "Description",
        ]
    )

    for host in selected_hosts:
        owners = host.get_owners(ids_only=True)
        users = User.objects.filter(Q(pk__in=owners[0]) | Q(groups__pk__in=owners[1]))
        usernames = ",".join(set([user.username for user in users]))
        emails = ",".join(set([user.email or "" for user in users]))

        recentIp = GulRecentArpByaddress.objects.filter(host=host).first()
        ip_history = recentIp.stopstamp if hasattr(recentIp, "stopstamp") else None

        recentMac = GulRecentArpBymac.objects.filter(host=host).first()
        mac_history = recentMac.stopstamp if hasattr(recentMac, "stopstamp") else None

        writer.writerow(
            [
                host.hostname,
                host.mac,
                host.expires,
                host.master_ip_address,
                mac_history,
                ip_history,
                usernames,
                emails,
                host.description,
            ]
        )

    return response


def change_perms_check(user, selected_hosts):
    selected_macs = [host.mac for host in selected_hosts]

    # Check for disabled hosts
    disabled_qs = Disabled.objects.filter(pk__in=selected_macs)
    if len(disabled_qs) != 0:
        return False

    # Check onwership of hosts for users with only object level permissions.
    host_perms_qs = Host.objects.filter(mac__in=selected_macs).by_change_perms(user)
    for host in selected_hosts:
        if host not in host_perms_qs:
            return False
    return True
