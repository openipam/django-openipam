from django.contrib import admin

from openipam.dns.models import DnsRecord, DnsType, Domain
# from openipam.dns.forms import DomainGroupPermissionForm, DomainUserPermissionForm, \
#     DnsTypeGroupPermissionForm, DnsTypeUserPermissionForm
from guardian.models import GroupObjectPermission, UserObjectPermission
import autocomplete_light


class BaseDNSAdmin(admin.ModelAdmin):
    """
        Hack override of methods to custimize app_label.
    """

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'app_label': 'DNS'
        })
        return super(BaseDNSAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def changelist_view(self, request, extra_context=None):
        cl = super(BaseDNSAdmin, self).changelist_view(request, extra_context)
        #assert False, cl.context_data
        cl.context_data.update({
            'app_label': 'DNS'
        })

        return cl


# class DomainGroupPermissionInline(admin.TabularInline):
#     model = DomainGroupObjectPermission
#     form = DomainGroupPermissionForm
#     extra = 1


# class DomainUserPermissionInline(admin.TabularInline):
#     model = DomainUserObjectPermission
#     form = DomainUserPermissionForm
#     extra = 1


class OpjectPermissionAdmin(BaseDNSAdmin):
    list_select_related = True

    def get_queryset(self, request):
        qs = super(OpjectPermissionAdmin, self).get_queryset(request)
        self.group_permissions = GroupObjectPermission.objects.filter(content_type__model=self.model._meta.model_name).cache()
        self.user_permissions = UserObjectPermission.objects.filter(content_type__model=self.model._meta.model_name).cache()
        return qs

    def sgroup_permissions(self, obj):
        perms_list = []
        perms = self.group_permissions.filter(object_pk=obj.pk)
        for perm in perms:
            perms_list.append('<span class="label label-info">%s: %s</span>' % (perm.group.name, perm.permission.codename))
        return '%s' % ' '.join(perms_list)
    sgroup_permissions.short_description = 'Group Permissions'
    sgroup_permissions.allow_tags = True

    def suser_permissions(self, obj):
        perms_list = []
        perms = self.user_permissions.filter(object_pk=obj.pk)
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
    #inlines = [DomainGroupPermissionInline, DomainUserPermissionInline]


# class DomainGroupObjectPermissionAdmin(admin.ModelAdmin):
#     list_display = ('group', 'content_object', 'permission',)
#     list_filter = ('group__name',)
#     search_fields = ('group__name', 'content_object__name',)
#     list_select_related = True
#     form = autocomplete_light.modelform_factory(DomainGroupObjectPermission)
#     change_form_template = 'admin/openipam/change_form.html'


# class DomainUserObjectPermissionAdmin(admin.ModelAdmin):
#     list_display = ('user', 'content_object', 'permission',)
#     search_fields = ('user__username', 'content_object__name',)
#     list_select_related = True
#     form = autocomplete_light.modelform_factory(DomainUserObjectPermission)
#     change_form_template = 'admin/openipam/change_form.html'


class DnsRecordAdmin(BaseDNSAdmin):
    list_display = ('name', 'dns_type', 'dns_view', 'ttl', 'priority', 'text_content', 'ip_content', 'edit_link')
    list_filter = ('dns_type', 'dns_view', 'priority', 'domain',)
    form = autocomplete_light.modelform_factory(DnsRecord)
    change_form_template = 'admin/openipam/change_form.html'
    list_editable = ('name', 'dns_type', 'text_content')
    list_display_links = ('edit_link',)
    #list_select_related = True
    search_fields = ('name', 'domain__name', 'text_content')

    def lookup_allowed(self, lookup, value):
        #assert False, lookup
        if 'address__host__mac' in lookup:
            return True
        return super(DnsRecordAdmin, self).lookup_allowed(lookup, value)

    def get_queryset(self, request):
        qs = super(DnsRecordAdmin, self).get_queryset(request)
        qs = qs.select_related('address', 'dns_type')

        return qs

    def ip_content(self, obj):
        return obj.address.address

    def edit_link(self, obj):
        return '<a href="%s">Edit</a>' % obj.pk
    edit_link.short_description = 'Edit'
    edit_link.allow_tags = True


# class DnsTypeGroupPermissionInline(admin.TabularInline):
#     model = DnsTypeGroupObjectPermission
#     form = DnsTypeGroupPermissionForm
#     extra = 1
#     #fk_name = 'content_object'


# class DnsTypeUserPermissionInline(admin.TabularInline):
#     model = DnsTypeUserObjectPermission
#     form = DnsTypeUserPermissionForm
#     extra = 1
#     #fk_name = 'content_object'


class DnsTypeAdmin(OpjectPermissionAdmin):
    list_display = ('name', 'description', 'min_permission', 'sgroup_permissions', 'suser_permissions')
    list_filter = ('min_permissions__name',)
    #inlines = [DnsTypeGroupPermissionInline, DnsTypeUserPermissionInline]

    def min_permission(self, obj):
        return '%s' % obj.min_permissions.name


admin.site.register(DnsType, DnsTypeAdmin)
admin.site.register(DnsRecord, DnsRecordAdmin)
admin.site.register(Domain, DomainAdmin)
# admin.site.register(DomainGroupObjectPermission, DomainGroupObjectPermissionAdmin)
# admin.site.register(DomainUserObjectPermission, DomainUserObjectPermissionAdmin)
