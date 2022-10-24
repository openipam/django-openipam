from django.contrib import admin

from openipam.dns.models import DnsRecord, DnsType, Domain, DnsView, DhcpDnsRecord
from openipam.dns.forms import DhcpDnsRecordForm
from openipam.core.admin import ChangedAdmin

from guardian.models import GroupObjectPermission, UserObjectPermission

#from autocomplete_light import shortcuts as al


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
                '<span class="label label-info">%s: %s</span>'
                % (perm.group.name, perm.permission.codename)
            )
        return "%s" % " ".join(perms_list)

    sgroup_permissions.short_description = "Group Permissions"
    sgroup_permissions.allow_tags = True

    def suser_permissions(self, obj):
        perms_list = []
        perms = [x for x in self.user_permissions if int(x.object_pk) == obj.pk]
        for perm in perms:
            perms_list.append(
                '<span class="label label-info">%s: %s</span>'
                % (perm.user.username, perm.permission.codename)
            )
        return "%s" % " ".join(perms_list)

    suser_permissions.short_description = "User Permissions"
    suser_permissions.allow_tags = True


class DomainAdmin(ObjectPermissionAdmin, ChangedAdmin):
    list_display = (
        "name",
        "sgroup_permissions",
        "suser_permissions",
        "changed_by",
        "changed",
    )
    #form = al.modelform_factory(Domain, exclude=("changed",))
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
    #form = al.modelform_factory(DnsRecord, exclude=("changed",))
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
        return '<a href="%s">Edit</a>' % obj.pk

    edit_link.short_description = "Edit"
    edit_link.allow_tags = True


class DhcpDnsRecordAdmin(admin.ModelAdmin):
    list_display = ("host", "ip_content", "domain", "ttl", "changed")
    search_fields = (
        "domain__name",
        "host__mac",
        "host__hostname",
        "ip_content__address",
    )
    form = DhcpDnsRecordForm


class DnsTypeAdmin(ObjectPermissionAdmin):
    list_display = ("name", "description", "sgroup_permissions", "suser_permissions")


admin.site.register(DnsView)
admin.site.register(DnsType, DnsTypeAdmin)
admin.site.register(DnsRecord, DnsRecordAdmin)
admin.site.register(DhcpDnsRecord, DhcpDnsRecordAdmin)
admin.site.register(Domain, DomainAdmin)
