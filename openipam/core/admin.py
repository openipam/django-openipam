from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect

from openipam.core.models import FeatureRequest
from openipam.core.actions import changed_delete_selected


class ChangedAdmin(admin.ModelAdmin):
    readonly_fields = ("changed_by",)

    def delete_model(self, request, obj):
        if getattr(obj, "changed_by"):
            obj.changed_by = request.user
            # TODO: Save overrides for these models so we can not set changed_by here
            try:
                obj.save(user=request.user)
            except Exception:
                obj.save()

        super(ChangedAdmin, self).delete_model(request, obj)

    def get_actions(self, request):
        actions = super(ChangedAdmin, self).get_actions(request)
        description = "Delete Selected %(verbose_name_plural)s"
        actions["delete_selected"] = (
            changed_delete_selected,
            "delete_selected",
            description,
        )

        return actions

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if getattr(obj, "changed_by"):
                obj.changed_by = request.user
                # TODO: Save overrides for these models so we can not set changed_by here
                try:
                    obj.save(user=request.user)
                except Exception:
                    obj.save()
        queryset.delete()

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(ChangedAdmin, self).save_model(request, obj, form, change)


class ReadOnlyAdmin(admin.ModelAdmin):
    actions = None
    list_display_links = None

    def change_view(self, request, object_id, form_url="", extra_context=None):
        opts = self.model._meta
        url = reverse(
            "admin:{app}_{model}_changelist".format(
                app=opts.app_label, model=opts.model_name
            )
        )
        return HttpResponseRedirect(url)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class FeatureRequestAdmin(admin.ModelAdmin):
    list_display = ("submitted", "comment", "full_user", "type", "is_complete")
    list_filter = ("type", "is_complete")
    search_fields = ("comment", "user__username")
    readonly_fields = ("user",)
    actions = ["mark_complete"]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def full_user(self, obj):
        return "%s (%s)" % (obj.user.get_full_name(), obj.user.username)

    full_user.short_description = "user"

    def mark_complete(self, request, queryset):
        queryset.update(is_complete=True)

    mark_complete.short_description = "Mark select as complete"


admin.site.register(FeatureRequest, FeatureRequestAdmin)
