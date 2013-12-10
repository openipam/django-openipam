from django.contrib import admin
from openipam.core.models import FeatureRequest
from openipam.core.forms import FeatureRequestForm


class FeatureRequestAdmin(admin.ModelAdmin):
    list_display = ('submitted', 'comment', 'user', 'type',)
    list_filter = ('type',)
    search_fields = ('comment', 'user__username')
    form = FeatureRequestForm

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


admin.site.register(FeatureRequest, FeatureRequestAdmin)
