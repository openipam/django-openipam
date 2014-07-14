from django.contrib import admin
from django import forms

from openipam.network.models import Network, NetworkRange, Address, Pool, DhcpGroup, \
    Pool, Vlan, AddressType, DefaultPool, DhcpOptionToDhcpGroup, Lease, DhcpOption, SharedNetwork, \
    NetworkToVlan
from openipam.network.forms import AddressTypeAdminForm, DhcpOptionToDhcpGroupAdminForm, AddressAdminForm
from openipam.core.admin import ChangedAdmin

import autocomplete_light


class NetworkAdmin(ChangedAdmin):
    form = autocomplete_light.modelform_factory(Network)
    list_display = ('nice_network', 'name', 'description', 'gateway')
    search_fields = ('network',)

    def nice_network(self, obj):
        url = str(obj.network).replace('/', '_2F')
        return '<a href="./%s/">%s</a>' % (url, obj.network)
    nice_network.short_description = 'Network'
    nice_network.allow_tags = True

    def save_model(self, request, obj, form, change):
        super(NetworkAdmin, self).save_model(request, obj, form, change)

        if not change:
            addresses = []
            for address in obj.network:
                reserved = False
                if address in (obj.gateway, obj.network[0], obj.network[-1]):
                    reserved = True
                addresses.append(
                    #TODO: Need to set pool eventually.
                    Address(address=address, network=obj, reserved=reserved, changed_by=request.user)
                )
            Address.objects.bulk_create(addresses)


class AddressTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'show_pool', 'show_ranges', 'is_default')
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


class DhcpGroupAdmin(ChangedAdmin):
    form = autocomplete_light.modelform_factory(DhcpGroup)


class DhcpOptionToDhcpGroupAdmin(ChangedAdmin):
    list_display = ('combined_value', 'changed', 'changed_by',)

    form = DhcpOptionToDhcpGroupAdminForm
    fields = ('group', 'option', 'readable_value', 'changed', 'changed_by',)
    readonly_fields = ('changed_by', 'changed',)

    def combined_value(self, obj):
        return '%s:%s=%r' % (obj.group.name, obj.option.name, str(obj.value))
    combined_value.short_description = 'Group:Option=Value'

    # def get_form(self, request, obj=None, **kwargs):
    #     super(DhcpOptionToDhcpGroupAdmin, self).get_form(request, obj, **kwargs)



class PoolAdmin(admin.ModelAdmin):
    pass


class SharedNetworkAdmin(ChangedAdmin):
    list_display = ('name', 'description', 'changed_by', 'changed',)


class VlanAdmin(ChangedAdmin):
    pass


class NetworkToVlanAdmin(ChangedAdmin):
    list_display = ('network', 'vlan', 'changed_by', 'changed',)


class LeaseAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Lease)
    list_display = ('address', 'mac', 'starts', 'ends', 'server', 'abandoned',)
    readonly_fields = ('starts', 'ends',)
    search_fields = ('address__address', 'host__mac', 'host__hostname',)

    def mac(self, obj):
        return obj.host_id
    mac.short_description = 'Host'


class HasHostFilter(admin.SimpleListFilter):
    title = 'has host'
    parameter_name = 'has_host'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(host__isnull=False)
        if self.value() == '0':
            return queryset.filter(host__isnull=True)


class AddressAdmin(ChangedAdmin):
    form = AddressAdminForm
    search_fields = ('address', 'host__mac', 'host__hostname',)
    list_filter = ('network', 'reserved', 'pool', HasHostFilter)
    list_display = ('address', 'network', 'host', 'pool', 'reserved', 'changed_by', 'changed')




admin.site.register(DefaultPool)
admin.site.register(NetworkToVlan, NetworkToVlanAdmin)
admin.site.register(SharedNetwork, SharedNetworkAdmin)
admin.site.register(DhcpOption)
admin.site.register(Vlan, ChangedAdmin)
admin.site.register(NetworkRange)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Lease, LeaseAdmin)
admin.site.register(AddressType, AddressTypeAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(DhcpGroup, DhcpGroupAdmin)
admin.site.register(DhcpOptionToDhcpGroup, DhcpOptionToDhcpGroupAdmin)
