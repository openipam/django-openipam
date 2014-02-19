from django.contrib import admin
from openipam.core.models import FeatureRequest
from openipam.core.forms import FeatureRequestForm


class FeatureRequestAdmin(admin.ModelAdmin):
    list_display = ('submitted', 'comment', 'full_user', 'type',)
    list_filter = ('type',)
    search_fields = ('comment', 'user__username')
    form = FeatureRequestForm

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def full_user(self, obj):
        return '%s (%s)' % (obj.user.get_full_name(), obj.user.username)
    full_user.short_description = 'user'


admin.site.register(FeatureRequest, FeatureRequestAdmin)
