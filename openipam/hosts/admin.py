from django.contrib import admin

from openipam.hosts.models import Host, Attribute, Disabled, GuestTicket, Notification, Attribute, Notification, \
    HostGroupObjectPermission, HostUserObjectPermission
from openipam.hosts.forms import HostGroupPermissionForm, HostUserPermissionForm

import autocomplete_light


class HostGroupPermissionInline(admin.TabularInline):
    model = HostGroupObjectPermission
    form = HostGroupPermissionForm
    extra = 1


class HostUserPermissionInline(admin.TabularInline):
    model = HostUserObjectPermission
    form = HostUserPermissionForm
    extra = 1


class HostAdmin(admin.ModelAdmin):
    list_display = ('nice_hostname', 'mac', 'dhcp_group', 'expires')
    list_filter = ('dhcp_group',)
    readonly_fields = ('changed_by', 'changed')
    search_fields = ('hostname', 'mac')
    inlines = [HostGroupPermissionInline, HostUserPermissionInline]

    # Null Foreign Keys dont get included by default
    def get_queryset(self, request):
        qs = super(HostAdmin, self).queryset(request)
        qs = qs.select_related('dhcp_group').all()
        return qs

    def nice_hostname(self, obj):
        return '<a href="./%s/">%s</a>' % (obj.mac, obj.hostname or 'N/A')
    nice_hostname.allow_tags = True
    nice_hostname.short_description = 'Hostname'
    nice_hostname.admin_order_field = 'hostname'


# class HostUserObjectPermissionAdmin(admin.ModelAdmin):
#     list_display = ('user', 'hostname', 'mac', 'permission',)
#     list_select_related = True
#     search_fields = ('user_username', 'content_object__mac', 'content_object__hostname')
#     form = autocomplete_light.modelform_factory(HostUserObjectPermission)
#     change_form_template = 'admin/openipam/change_form.html'

#     def hostname(self, obj):
#         return '%s' % obj.content_object.hostname

#     def mac(self, obj):
#         return '%s' % obj.content_object.mac


# class HostGroupObjectPermissionAdmin(admin.ModelAdmin):
#     list_display = ('group', 'hostname', 'mac', 'permission',)
#     list_filter = ('group__name',)
#     search_fields = ('group__name', 'content_object__mac', 'content_object__hostname')
#     list_select_related = True
#     form = autocomplete_light.modelform_factory(HostGroupObjectPermission)
#     change_form_template = 'admin/openipam/change_form.html'

#     def hostname(self, obj):
#         return '%s' % obj.content_object.hostname

#     def mac(self, obj):
#         return '%s' % obj.content_object.mac


class DisabledAdmin(admin.ModelAdmin):
    list_display = ('mac', 'disabled', 'disabled_by_full',)
    form = autocomplete_light.modelform_factory(Disabled)
    change_form_template = 'admin/openipam/change_form.html'
    list_select_related = True

    def disabled_by_full(self, obj):
        return '%s (%s)' % (obj.disabled_by.username, obj.disabled_by.get_full_name())
    disabled_by_full.short_description = 'Disabled By'

class GuestTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'starts', 'ends')
    list_filter = ('starts', 'ends')
    search_fields = ('uid', 'ticket')
    form = autocomplete_light.modelform_factory(GuestTicket)
    change_form_template = 'admin/openipam/change_form.html'


admin.site.register(Host, HostAdmin)
# admin.site.register(HostUserObjectPermission, HostUserObjectPermissionAdmin)
# admin.site.register(HostGroupObjectPermission, HostGroupObjectPermissionAdmin)
admin.site.register(Attribute)
admin.site.register(Disabled, DisabledAdmin)
admin.site.register(GuestTicket, GuestTicketAdmin)
