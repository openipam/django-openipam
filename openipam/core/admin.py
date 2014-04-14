from django.contrib import admin
from openipam.core.models import FeatureRequest


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
