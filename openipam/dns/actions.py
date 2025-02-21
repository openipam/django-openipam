from django.contrib import messages
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.core import serializers

from openipam.dns.models import DnsRecord


def delete_records(request, selected_records):
    user = request.user

    # Must have global delete perm or object owner perm
    if not user.has_perm("dns.delete_dnsrecord") and not change_perms_check(
        user, selected_records
    ):
        messages.error(
            request,
            "You do not have permissions to perform this action on one or more the selected dns records. "
            "Please contact an IPAM administrator.",
        )
    else:
        dns_records = DnsRecord.objects.filter(pk__in=selected_records)

        # Log Deletion
        for record in selected_records:
            data = serializers.serialize(
                "json", [x for x in dns_records if x.pk == int(record)]
            )
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(DnsRecord).pk,
                object_id=record,
                object_repr=force_text(DnsRecord.objects.get(pk=record)),
                action_flag=DELETION,
                change_message=data,
            )

        dns_records.delete()
        messages.success(request, "Selected DNS records have been deleted.")


# def change_perms_check(user, selected_records):
#     # Check permission of dnsrecords for users with only object level permissions.
#     allowed_dnsrecords = DnsRecord.objects.filter(
#         pk__in=selected_records
#     ).by_change_perms(user_or_group=user, ids_only=True)
#     for record in selected_records:
#         if int(record) not in allowed_dnsrecords:
#             return False
#     return True


def change_perms_check(user, selected_records):
    # Check to makre sure records and perms match
    dns_perms_qs = DnsRecord.objects.filter(pk__in=selected_records).by_change_perms(
        user
    )
    if len(selected_records) != len(dns_perms_qs):
        return False
    return True
