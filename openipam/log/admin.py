from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from django.utils.timezone import localtime
from django import forms

from openipam.log.models import HostLog, EmailLog, DnsRecordLog, AddressLog, UserLog

# from dal import autocomplete
from autocomplete_light import shortcuts as al

User = get_user_model()


class LogEntryAdminForm(forms.ModelForm):
    # user = forms.ModelChoiceField(
    #     queryset=User.objects.all(),
    #     widget=autocomplete.ModelSelect2(url="user_autocomplete"),
    # )
    # content_type = forms.ModelChoiceField(
    #     queryset=ContentType.objects.all(),
    #     widget=autocomplete.ModelSelect2(url="content_type_autocomplete"),
    # )
    user = al.ModelChoiceField("UserAutocomplete")
    content_type = al.ModelChoiceField("ContentTypeAutocomplete")

    class Meta:
        model = LogEntry
        exclude = ("user", "content_type")


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("object_name", "object_id", "action_name", "user", "change_time")
    list_filter = ("action_time",)
    search_fields = ("object_repr", "object_id", "user__username")
    form = LogEntryAdminForm
    list_select_related = True

    def get_queryset(self, request):
        qs = super(LogEntryAdmin, self).get_queryset(request)
        return qs.select_related("content_type", "user")

    def change_time(self, obj):
        return '<span class="nowrap">%s</span>' % localtime(obj.action_time).strftime(
            "%d %b %Y %H:%M:%S"
        )

    change_time.short_description = "Timestamp"
    change_time.admin_order_field = "action_time"
    change_time.allow_tags = True

    def action_name(self, obj):
        if obj.action_flag == 1:
            return "Addition"
        elif obj.action_flag == 2:
            return "Changed"
        elif obj.action_flag == 3:
            return "Deletion"

    action_name.short_description = "Action"

    def object_name(self, obj):
        return "%s: %s" % (obj.content_type.model.capitalize(), obj.object_repr)

    object_name.short_description = "Model object"


class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("to", "when", "subject")
    list_filter = ("when",)
    readonly_fields = ("when", "to", "subject", "email_body")
    search_fields = ("subject", "body", "to")
    exclude = ("body",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        # Return nothing to make sure user can't update any data
        pass


class HostLogAdmin(admin.ModelAdmin):
    list_display = ("mac", "hostname", "changed", "nice_changed_by")
    search_fields = ("mac", "hostname", "changed_by__username")
    list_select_related = True
    readonly_fields = ("changed_by",)

    def nice_changed_by(self, obj):
        href = '<a href="%s">%s (%s)</a>'

        username = obj.changed_by.username
        if obj.changed_by.first_name and obj.changed_by.last_name:
            full_name = obj.changed_by.get_full_name()
        else:
            full_name = ""

        return href % (
            reverse_lazy("admin:user_user_change", args=[obj.changed_by.pk]),
            full_name,
            username,
        )

    nice_changed_by.short_description = "Changed By"
    nice_changed_by.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        # Return nothing to make sure user can't update any data
        pass


class DnsRecordLogAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "ttl",
        "dns_type",
        "priority",
        "ip_content",
        "changed",
        "nice_changed_by",
    )
    search_fields = (
        "name",
        "dns_type",
        "ttl",
        "priority",
        "ip_content",
        "changed_by__username",
    )
    list_select_related = True
    readonly_fields = ("changed_by",)

    def nice_changed_by(self, obj):
        href = '<a href="%s">%s (%s)</a>'

        username = obj.changed_by.username
        if obj.changed_by.first_name and obj.changed_by.last_name:
            full_name = obj.changed_by.get_full_name()
        else:
            full_name = ""

        return href % (
            reverse_lazy("admin:user_user_change", args=[obj.changed_by.pk]),
            full_name,
            username,
        )

    nice_changed_by.short_description = "Changed By"
    nice_changed_by.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        # Return nothing to make sure user can't update any data
        pass


class AddressLogAdmin(admin.ModelAdmin):
    list_display = (
        "address",
        "network",
        "host",
        "pool_name",
        "reserved",
        "nice_changed_by",
        "changed",
    )
    search_fields = ("address", "network", "changed_by__username")
    list_select_related = True
    readonly_fields = ("changed_by",)

    def nice_changed_by(self, obj):
        href = '<a href="%s">%s (%s)</a>'

        username = obj.changed_by.username
        if obj.changed_by.first_name and obj.changed_by.last_name:
            full_name = obj.changed_by.get_full_name()
        else:
            full_name = ""

        return href % (
            reverse_lazy("admin:user_user_change", args=[obj.changed_by.pk]),
            full_name,
            username,
        )

    nice_changed_by.short_description = "Changed By"
    nice_changed_by.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        # Return nothing to make sure user can't update any data
        pass


class UserLogAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "full_name",
        "email",
        "is_staff",
        "is_superuser",
        "is_ipamadmin",
        "source",
        "last_login",
    )
    search_fields = ("username", "email")
    list_select_related = True

    def full_name(self, obj):
        first_name = "" if obj.first_name is None else obj.first_name
        last_name = "" if obj.last_name is None else obj.last_name
        return "%s %s" % (first_name, last_name)

    full_name.admin_order_field = "last_name"

    def is_ipamadmin(self, obj):
        return obj.is_ipamadmin

    is_ipamadmin.short_description = "IPAM Admin Status"
    is_ipamadmin.boolean = True


admin.site.disable_action("delete_selected")
admin.site.register(EmailLog, EmailLogAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(HostLog, HostLogAdmin)
admin.site.register(DnsRecordLog, DnsRecordLogAdmin)
admin.site.register(AddressLog, AddressLogAdmin)
admin.site.register(UserLog, UserLogAdmin)
