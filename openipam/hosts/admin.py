from django.contrib import admin

# from django.forms import modelform_factory

from openipam.hosts.models import (
    Host,
    Attribute,
    Disabled,
    GuestTicket,
    ExpirationType,
    StructuredAttributeValue,
    # AttributeToHost,
    # StructuredAttributeToHost,
    Notification,
    OUI,
)
from openipam.hosts.forms import (
    ExpirationTypeAdminForm,
    HostDisableForm,
    # AttributeForm,
    StructuredAttributeValueForm,
)
from openipam.core.admin import ChangedAdmin

# from dal import autocomplete
# from autocomplete_light import shortcuts as al

from guardian.admin import GuardedModelAdmin


class HostAdmin(ChangedAdmin):
    list_display = (
        "nice_hostname",
        "mac",
        "dhcp_group",
        "expires",
        "changed_by",
        "changed",
    )
    list_filter = ("dhcp_group",)
    readonly_fields = ("changed_by", "changed")
    search_fields = ("hostname",)
    # inlines = [HostGroupPermissionInline, HostUserPermissionInline]

    # Null Foreign Keys dont get included by default
    def get_queryset(self, request):
        qs = super(HostAdmin, self).get_queryset(request)
        qs = qs.select_related("dhcp_group").all()
        return qs

    def nice_hostname(self, obj):
        return '<a href="./%s/">%s</a>' % (obj.mac, obj.hostname or "N/A")

    nice_hostname.allow_tags = True
    nice_hostname.short_description = "Hostname"
    nice_hostname.admin_order_field = "hostname"


class DisabledAdmin(ChangedAdmin):
    list_display = ("mac", "hostname", "reason", "changed", "changed_by")
    form = HostDisableForm
    list_select_related = True
    search_fields = ("mac", "changed_by__username")

    def save_model(self, request, obj, form, change):
        data = form.cleaned_data
        obj.mac = data["mac"]
        super(DisabledAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(DisabledAdmin, self).get_queryset(request)
        qs = qs.extra(
            select={
                "hostname": "SELECT hostname from hosts where hosts.mac = disabled.mac"
            }
        )
        return qs

    def hostname(self, obj):
        return "%s" % obj.hostname

    hostname.short_description = "Hostname"


class GuestTicketAdmin(admin.ModelAdmin):
    list_display = ("ticket", "user", "starts", "ends")
    list_filter = ("starts", "ends")
    search_fields = ("user__username", "ticket")
    autocomplete_fields = ("user",)
    # form = modelform_factory(
    #     GuestTicket,
    #     fields=("user", "ticket", "starts", "ends", "description"),
    #     widgets={"user": autocomplete.ModelSelect2(url="user_autocomplete")},
    # )
    # form = al.modelform_factory(
    #     GuestTicket, fields=("user", "ticket", "starts", "ends", "description")
    # )


class StructuredAttributeValueInline(admin.TabularInline):
    model = StructuredAttributeValue
    form = StructuredAttributeValueForm


class AttributeAdmin(ChangedAdmin):
    search_fields = ("name",)
    # form = AttributeForm
    inlines = [StructuredAttributeValueInline]


class ExpirationTypeAdmin(GuardedModelAdmin):
    form = ExpirationTypeAdminForm

    # Hack for guardian 1.8 bug
    def __init__(self, *args, **kwargs):
        self.queryset = super(ExpirationTypeAdmin, self).get_queryset
        super(ExpirationTypeAdmin, self).__init__(*args, **kwargs)


class StructuredAttributeValueAdmin(ChangedAdmin):
    list_display = ("attribute", "value", "is_default", "changed_by", "changed")
    list_filter = ("attribute__name",)
    autocomplete_fields = ("attribute",)


admin.site.register(Host, HostAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(StructuredAttributeValue, StructuredAttributeValueAdmin)
admin.site.register(Notification)
admin.site.register(ExpirationType, ExpirationTypeAdmin)
admin.site.register(Disabled, DisabledAdmin)
admin.site.register(GuestTicket, GuestTicketAdmin)
admin.site.register(OUI)
