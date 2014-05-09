from django.contrib import admin

from openipam.core.models import FeatureRequest
from openipam.core.actions import changed_delete_selected


class ChangedAdmin(admin.ModelAdmin):
    readonly_fields = ('changed_by',)

    def delete_model(self, request, obj):
        if getattr(obj, 'changed_by'):
            obj.changed_by = request.user
            obj.save()

        super(ChangedAdmin, self).delete_model(request, obj)

    def get_actions(self, request):
        actions = super(ChangedAdmin, self).get_actions(request)
        description = 'Delete Selected %(verbose_name_plural)s'
        actions['delete_selected'] = (changed_delete_selected, 'delete_selected', description)

        return actions

    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        super(ChangedAdmin, self).save_model(request, obj, form, change)



class FeatureRequestAdmin(admin.ModelAdmin):
    list_display = ('submitted', 'comment', 'full_user', 'type', 'is_complete',)
    list_filter = ('type', 'is_complete')
    search_fields = ('comment', 'user__username')
    readonly_fields = ('user',)
    actions = ['mark_complete']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def full_user(self, obj):
        return '%s (%s)' % (obj.user.get_full_name(), obj.user.username)
    full_user.short_description = 'user'

    def mark_complete(self, request, queryset):
        queryset.update(is_complete=True)
    mark_complete.short_description = "Mark select as complete"


admin.site.register(FeatureRequest, FeatureRequestAdmin)
