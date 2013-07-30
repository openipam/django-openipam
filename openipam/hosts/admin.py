from django.contrib import admin
from models import Host, Attribute, Disabled, GuestTicket, Notification, Attribute, Notification
from guardian.admin import GuardedModelAdmin


class HostAdmin(GuardedModelAdmin):
    list_display = ('nice_hostname', 'mac', 'dhcp_group', 'expires')
    list_filter = ('dhcp_group',)
    readonly_fields = ('changed_by', 'changed')
    search_fields = ('hostname', 'mac')

    # Null Foreign Keys dont get included by default
    def queryset(self, request):
        qs = super(HostAdmin, self).queryset(request)
        qs = qs.select_related('dhcp_group').all()
        return qs

    def nice_hostname(self, obj):
        return '<a href="./%s/">%s</a>' % (obj.mac, obj.hostname)
    nice_hostname.allow_tags = True
    nice_hostname.short_description = 'Hostname'
    nice_hostname.admin_order_field = 'hostname'


class DisabledAdmin(admin.ModelAdmin):
    list_display = ('mac',)
    readonly_fields = ('disabled', 'disabled_by')


class GuestTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'uid', 'starts', 'ends')
    list_filter = ('starts', 'ends')
    search_fields = ('uid', 'ticket')


admin.site.register(Host, HostAdmin)
admin.site.register(Attribute)
admin.site.register(Disabled, DisabledAdmin)
admin.site.register(GuestTicket, GuestTicketAdmin)
admin.site.register(Notification)
