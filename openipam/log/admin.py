from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django import forms

import autocomplete_light

User = get_user_model()


class LogEntryAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(User.objects.all(),
        widget=autocomplete_light.ChoiceWidget('UserAutocomplete'))
    content_type = forms.ModelChoiceField(ContentType.objects.all(),
        widget=autocomplete_light.ChoiceWidget('ContentTypeAutocomplete'))


    class Meta:
        model = LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('object_name', 'object_id', 'action_name', 'user')
    form = LogEntryAdminForm

    def get_queryset(self, request):
        qs = super(LogEntryAdmin, self).get_queryset(request)
        return qs.select_related('content_type')

    def action_name(self, obj):
        if obj.action_flag == 1:
            return 'Addition'
        elif obj.action_flag == 2:
            return 'Changed'
        elif obj.action_flag == 3:
            return 'Deletion'
    action_name.short_description = 'Action'

    def object_name(self, obj):
        return '%s: %s' % (obj.content_type.model.capitalize(), obj.object_repr)
    object_name.short_description = 'Model object'

admin.site.register(LogEntry, LogEntryAdmin)
