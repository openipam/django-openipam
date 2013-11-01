from django.contrib import admin

from openipam.dns.models import DnsRecord, DnsType, Domain, DomainGroupObjectPermission, DomainUserObjectPermission, \
    DnsTypeGroupObjectPermission, DnsTypeUserObjectPermission
from openipam.dns.forms import DomainGroupPermissionForm, DomainUserPermissionForm, \
    DnsTypeGroupPermissionForm, DnsTypeUserPermissionForm

import autocomplete_light


class DomainGroupPermissionInline(admin.TabularInline):
    model = DomainGroupObjectPermission
    form = DomainGroupPermissionForm
    extra = 1


class DomainUserPermissionInline(admin.TabularInline):
    model = DomainUserObjectPermission
    form = DomainUserPermissionForm
    extra = 1


class OpjectPermissionAdmin(admin.ModelAdmin):
    list_select_related = True

    def get_queryset(self, request):
        qs = super(OpjectPermissionAdmin, self).get_queryset(request)
        qs = qs.prefetch_related('group_permissions__group', 'user_permissions__user',
                                 'group_permissions__permission', 'user_permissions__permission')

        return qs

    def sgroup_permissions(self, obj):
        perms_list = []
        perms = obj.group_permissions.all()
        for perm in perms:
            perms_list.append('<span class="label label-info">%s: %s</span>' % (perm.group.name, perm.permission.codename))
        return '%s' % ' '.join(perms_list)
    sgroup_permissions.short_description = 'Group Permissions'
    sgroup_permissions.allow_tags = True

    def suser_permissions(self, obj):
        perms_list = []
        perms = obj.user_permissions.all()
        for perm in perms:
            perms_list.append('<span class="label label-info">%s: %s</span>' % (perm.user.username, perm.permission.codename))
        return '%s' % ' '.join(perms_list)
    suser_permissions.short_description = 'User Permissions'
    suser_permissions.allow_tags = True


class DomainAdmin(OpjectPermissionAdmin):
    list_display = ('name', 'sgroup_permissions', 'suser_permissions')
    form = autocomplete_light.modelform_factory(Domain)
    change_form_template = 'admin/openipam/change_form.html'
    search_fields = ('name',)
    inlines = [DomainGroupPermissionInline, DomainUserPermissionInline]


class DomainGroupObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'content_object', 'permission',)
    list_filter = ('group__name',)
    search_fields = ('group__name', 'content_object__name',)
    list_select_related = True
    form = autocomplete_light.modelform_factory(DomainGroupObjectPermission)
    change_form_template = 'admin/openipam/change_form.html'


class DomainUserObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_object', 'permission',)
    search_fields = ('user__username', 'content_object__name',)
    list_select_related = True
    form = autocomplete_light.modelform_factory(DomainUserObjectPermission)
    change_form_template = 'admin/openipam/change_form.html'


class DnsRecordAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'dns_type', 'dns_view', 'ttl', 'priority', 'text_content')
    list_filter = ('dns_type', 'domain',)
    form = autocomplete_light.modelform_factory(DnsRecord)
    change_form_template = 'admin/openipam/change_form.html'
    #list_editable = ('domain', 'dns_type', 'dns_view', 'ttl', 'priority', 'text_content')
    #list_select_related = True
    search_fields = ('name', 'domain__name', 'text_content')


class DnsTypeGroupPermissionInline(admin.TabularInline):
    model = DnsTypeGroupObjectPermission
    form = DnsTypeGroupPermissionForm
    extra = 1
    #fk_name = 'content_object'

class DnsTypeUserPermissionInline(admin.TabularInline):
    model = DnsTypeUserObjectPermission
    form = DnsTypeUserPermissionForm
    extra = 1
    #fk_name = 'content_object'


class DnsTypeAdmin(OpjectPermissionAdmin):
    list_display = ('name', 'description', 'min_permission', 'sgroup_permissions', 'suser_permissions')
    list_filter = ('min_permissions__name',)
    inlines = [DnsTypeGroupPermissionInline, DnsTypeUserPermissionInline]

    def min_permission(self, obj):
        return '%s' % obj.min_permissions.name


admin.site.register(DnsType, DnsTypeAdmin)
admin.site.register(DnsRecord, DnsRecordAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(DomainGroupObjectPermission, DomainGroupObjectPermissionAdmin)
admin.site.register(DomainUserObjectPermission, DomainUserObjectPermissionAdmin)
