from django.contrib import admin
from openipam.core.models import FeatureRequest
from openipam.core.forms import FeatureRequestAdminForm


class FeatureRequestAdmin(admin.ModelAdmin):
    list_display = ('submitted', 'comment', 'user', 'type',)
    list_filter = ('type', 'user',)
    search_fields = ('comment',)
    form = FeatureRequestAdminForm

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


admin.site.register(FeatureRequest, FeatureRequestAdmin)
