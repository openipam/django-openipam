from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from openipam.dns.models import DnsRecord


def delete_records(request, selected_records):
    user = request.user

    # Must have global delete perm or object owner perm
    if not user.has_perm('dns.delete_dnsrecord') and not change_perms_check(user, selected_records):
        messages.error(request, "You do not have permissions to perform this action on one or more the selected hosts. "
                       "Please contact an IPAM administrator.")
    else:
        # Log Deletion
        for record in selected_records:
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(DnsRecord).pk,
                object_id=record,
                object_repr=force_unicode(DnsRecord.objects.get(pk=record)),
                action_flag=DELETION
            )

        DnsRecord.objects.filter(pk__in=selected_records).delete()

        messages.success(request, "Selected DNS records have been deleted.")


def change_perms_check(user, records):
    # Check permission of dnsrecords for users with only object level permissions.
    user_perms_check = False
    allowed_dnsrecords = DnsRecord.objects.filter(pk__in=records).by_change_perms(user).values_list('pk', flat=True)
    user_perm_list = [True if record.pk in allowed_dnsrecords else False for record in records]
    if set(user_perm_list) == set([True]):
        user_perms_check = True

    return user_perms_check
