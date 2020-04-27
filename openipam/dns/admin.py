from django.contrib import admin
from django.forms import modelform_factory
from django.utils.safestring import mark_safe
from django.urls import reverse

from openipam.dns.models import (
    DnsRecord,
    DnsType,
    Domain,
    DnsView,
    DhcpDnsRecord,
    PdnsZoneXfer,
    DnsRecordMunged,
)
from openipam.dns.forms import DhcpDnsRecordForm
from openipam.core.admin import ChangedAdmin, ReadOnlyAdmin

from guardian.models import GroupObjectPermission, UserObjectPermission


class ObjectPermissionAdmin(admin.ModelAdmin):
    list_select_related = True

    def get_queryset(self, request):
        qs = super(ObjectPermissionAdmin, self).get_queryset(request)
        self.group_permissions = GroupObjectPermission.objects.select_related(
            "group", "permission"
        ).filter(content_type__model=self.model._meta.model_name)
        self.user_permissions = UserObjectPermission.objects.select_related(
            "user", "permission"
        ).filter(content_type__model=self.model._meta.model_name)
        return qs

    def sgroup_permissions(self, obj):
        perms_list = []
        perms = [x for x in self.group_permissions if int(x.object_pk) == obj.pk]
        for perm in perms:
            perms_list.append(
                '<a href="%s">%s: %s</a>'
                % (
                    reverse("admin:user_groupobjectpermission_change", args=[perm.pk]),
                    perm.group.name,
                    perm.permission.codename,
                )
            )
        return mark_safe("%s" % "\n".join(perms_list))

    sgroup_permissions.short_description = "Group Permissions"

    def suser_permissions(self, obj):
        perms_list = []
        perms = [x for x in self.user_permissions if int(x.object_pk) == obj.pk]
        for perm in perms:
            perms_list.append(
                '<a href="%s">%s: %s</a>'
                % (
                    reverse("admin:user_userobjectpermission_change", args=[perm.pk]),
                    perm.user.username,
                    perm.permission.codename,
                )
            )
        return mark_safe("%s" % "\n".join(perms_list))

    suser_permissions.short_description = "User Permissions"


class DomainAdmin(ObjectPermissionAdmin, ChangedAdmin):
    list_display = (
        "name",
        "sgroup_permissions",
        "suser_permissions",
        "changed_by",
        "changed",
    )
    form = modelform_factory(Domain, exclude=("changed",))
    search_fields = ("name",)


class DnsRecordAdmin(ChangedAdmin):
    list_display = (
        "name",
        "dns_type",
        "dns_view",
        "ttl",
        "priority",
        "text_content",
        "ip_content",
        "edit_link",
    )
    list_filter = ("dns_type", "dns_view", "priority", "domain")
    form = modelform_factory(DnsRecord, exclude=("changed",))
    list_editable = ("name", "dns_type", "text_content")
    list_display_links = ("edit_link",)
    # list_select_related = True
    search_fields = ("name", "domain__name", "text_content")

    def lookup_allowed(self, lookup, value):
        if "address__host__mac" in lookup:
            return True
        return super(DnsRecordAdmin, self).lookup_allowed(lookup, value)

    def get_queryset(self, request):
        qs = super(DnsRecordAdmin, self).get_queryset(request)
        qs = qs.select_related("ip_content", "dns_type")

        return qs

    def ip_content(self, obj):
        return obj.address.address

    def edit_link(self, obj):
        return mark_safe(f'<a href="{obj.pk}">Edit</a>')

    edit_link.short_description = "Edit"


class DhcpDnsRecordAdmin(admin.ModelAdmin):
    list_display = ("host", "ip_content", "domain", "ttl", "changed")
    search_fields = (
        "domain__name",
        "host__mac",
        "host__hostname",
        "ip_content__address",
    )
    autocomplete_fields = ("domain",)
    list_select_related = True
    form = DhcpDnsRecordForm

    def get_queryset(self, *args, **kwargs):
        return (
            super(DhcpDnsRecordAdmin, self)
            .get_queryset(*args, **kwargs)
            .select_related("ip_content", "host", "domain")
        )


class DnsTypeAdmin(ObjectPermissionAdmin):
    list_display = ("name", "description", "sgroup_permissions", "suser_permissions")


class PdnsZoneXferAdmin(ReadOnlyAdmin):
    list_display = (
        "domain",
        "name",
        "type",
        "content",
        "ttl",
        "priority",
        "change_date",
    )
    list_select_related = True
    list_filter = ("type",)
    search_fields = ("domain__name", "name", "content")


# class SupermasterAdmin(ChangedAdmin):
#     list_display = ("ip", "nameserver", "account", "changed_by", "changed")
#     list_select_related = True


class DnsRecordMungedAdmin(ReadOnlyAdmin):
    list_display = (
        "domain",
        "name",
        "type",
        "content",
        "ttl",
        "prio",
        "change_date",
        "dns_view",
    )
    list_select_related = True
    list_filter = ("type",)
    search_fields = ("domain__name", "name", "content")

    def get_queryset(self, *args, **kwargs):
        return (
            super(DnsRecordMungedAdmin, self)
            .get_queryset(*args, **kwargs)
            .select_related("domain")
        )


admin.site.register(DnsView)
admin.site.register(DnsType, DnsTypeAdmin)
admin.site.register(DnsRecord, DnsRecordAdmin)
admin.site.register(DhcpDnsRecord, DhcpDnsRecordAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(PdnsZoneXfer, PdnsZoneXferAdmin)
admin.site.register(DnsRecordMunged, DnsRecordMungedAdmin)
