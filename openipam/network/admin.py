from django.contrib import admin

from openipam.network.models import Network, NetworkRange, Address, Pool, DhcpGroup, \
    Pool, Vlan, AddressType, DefaultPool
from openipam.network.forms import AddressTypeAdminForm

import autocomplete_light


class NetworkAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Network)
    change_form_template = 'admin/openipam/change_form.html'
    #list_display = ('network', 'name', 'description', 'gateway')

    # def nice_network(self, obj):
    #     url = str(obj.network).replace('/', '_2F')
    #     return '<a href="./%s/">%s</a>' % (url, obj.network)
    # nice_network.short_description = 'Network'
    # nice_network.allow_tags = True


class AddressTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'show_pool', 'show_ranges')
    form = AddressTypeAdminForm
    list_select_related = True

    def show_pool(self, obj):
        return obj.pool if obj.pool else ''
    show_pool.short_description = 'Network Pool'

    def show_ranges(self, obj):
        ranges = [str(range) for range in obj.ranges.all()]
        return '%s' % '<br />'.join(ranges) if ranges else ''
    show_ranges.short_description = 'Network Ranges'
    show_ranges.allow_tags = True


class DhcpGroupAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(DhcpGroup)


class PoolAdmin(admin.ModelAdmin):
    pass


class AddressAdmin(admin.ModelAdmin):
    list
    form = autocomplete_light.modelform_factory(Address)
    search_fields = ('address',)


admin.site.register(DefaultPool)
admin.site.register(Vlan)
admin.site.register(NetworkRange)
admin.site.register(Network, NetworkAdmin)
admin.site.register(AddressType, AddressTypeAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(DhcpGroup, DhcpGroupAdmin)
