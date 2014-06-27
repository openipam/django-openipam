from django.contrib import admin

from openipam.hosts.models import Host, Attribute, Disabled, GuestTicket, Attribute, StructuredAttributeValue
from openipam.core.admin import ChangedAdmin

import autocomplete_light


class HostAdmin(ChangedAdmin):
    list_display = ('nice_hostname', 'mac', 'dhcp_group', 'expires', 'changed_by', 'changed')
    list_filter = ('dhcp_group',)
    readonly_fields = ('changed_by', 'changed')
    search_fields = ('hostname', 'mac')
    #inlines = [HostGroupPermissionInline, HostUserPermissionInline]

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


class DisabledAdmin(ChangedAdmin):
    list_display = ('host', 'reason', 'changed', 'changed_by_full',)
    form = autocomplete_light.modelform_factory(Disabled)
    list_select_related = True

    def changed_by_full(self, obj):
        return '%s (%s)' % (obj.changed_by.username, obj.changed_by.get_full_name())
    changed_by_full.short_description = 'Changed By'


class GuestTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'starts', 'ends')
    list_filter = ('starts', 'ends')
    search_fields = ('uid', 'ticket')
    form = autocomplete_light.modelform_factory(GuestTicket)


class AttributeAdmin(ChangedAdmin):
    pass


class StructuredAttributeValueAdmin(ChangedAdmin):
    list_display = ('attribute', 'value', 'is_default', 'changed_by', 'changed',)
    list_filter = ('attribute__name',)


admin.site.register(Host, HostAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(StructuredAttributeValue, StructuredAttributeValueAdmin)
#admin.site.register(Notification)
admin.site.register(Disabled, DisabledAdmin)
admin.site.register(GuestTicket, GuestTicketAdmin)
