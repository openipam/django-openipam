from django.contrib import admin
from django.apps import apps


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


app = apps.get_app_config('firewall')

for model_name, model in app.models.items():
    if not model_name.endswith('base') and not model_name.endswith('log'):
        print model_name
        admin.site.register(model, DynamicColumnAdmin)
