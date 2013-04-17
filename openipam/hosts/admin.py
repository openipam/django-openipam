from django.contrib import admin
from models import Host, Attribute, Disabled, GuestTicket, Notification, Attribute



class HostAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'mac', 'dhcp_group', 'expires')
    list_filter = ('dhcp_group',)
    readonly_fields = ('changed_by', 'changed')
    search_fields = ('hostname', 'mac')

    # Null Foreign Keys dont get included by default
    def queryset(self, request):
        qs = super(HostAdmin, self).queryset(request)
        qs = qs.select_related('dhcp_group').all()
        return qs


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
