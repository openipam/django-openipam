from django.contrib import admin
from models import Host


class HostAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'mac')
    exclude = ('changed_by',)


admin.site.register(Host, HostAdmin)
