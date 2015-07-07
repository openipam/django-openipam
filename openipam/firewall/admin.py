from django.contrib import admin
from django.apps import apps

from openipam.firewall.models import Rule

app = apps.get_app_config('firewall')



class DynamicColumnAdmin(admin.ModelAdmin):
    # list_filter_names = ['chain', 'target', 'src', 'dst', ]
    list_filter_names = ['chain', 'target', ]
    search_fields_if_present = {
        'chain': ['chain__name'],
        'target': ['target__name'],
        'src': ['src__name', 'src__host'],
        'dst': ['dst__name', 'dst__host'],
        'description': ['description'],
    }

    def __init__(self, *args, **kwargs):
        super(DynamicColumnAdmin, self).__init__(*args, **kwargs)
        field_list = [i.name for i in self.model._meta.fields]
        self.list_display = field_list
        self.list_display_links = field_list[0]
        self.list_filter = []
        self.search_fields = []
        for n in field_list:
            if n in self.list_filter_names:
                self.list_filter.append(n)
            if n in self.search_fields_if_present:
                self.search_fields.extend(self.search_fields_if_present[n])


class SelectRelatedAdmin(admin.ModelAdmin):
    select_related_columns = ()

    def get_queryset(self, request):
        qs = super(SelectRelatedAdmin, self).get_queryset(request)
        return qs.select_related(*self.select_related_columns)


class RuleAdmin(SelectRelatedAdmin):
    search_fields = ('chain__name', 'target__name', 'src__host', 'src__name', 'dst__host', 'dst__name', 'description')
    list_filter = ('chain__name', 'target__name')
    select_related_columns = ('chain__tbl', 'if_in', 'if_out', 'proto', 'src', 'sport', 'dst', 'dport', 'target__tbl', 'created_for')

    def get_list_display(self, request):
        return ['id'] + self.get_fields(request)


for model_name, model in app.models.items():
    if not model_name.endswith('base') and not model_name.endswith('log') and not model_name in ['rule']:
        admin.site.register(model, DynamicColumnAdmin)

admin.site.register(Rule, RuleAdmin)
