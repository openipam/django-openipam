from django.contrib import admin
from django.apps import apps

from openipam.firewall.models import Rule


app = apps.get_app_config("firewall")


class DynamicColumnAdmin(admin.ModelAdmin):
    list_display = ()

    def __init__(self, *args, **kwargs):
        super(DynamicColumnAdmin, self).__init__(*args, **kwargs)
        mfields = self.model._meta.fields
        mfield_names = [i.name for i in mfields]

        if not self.list_display:
            self.list_display = mfield_names


class SelectRelatedAdmin(admin.ModelAdmin):
    select_related_columns = ()

    def get_queryset(self, request):
        qs = super(SelectRelatedAdmin, self).get_queryset(request)
        if self.select_related_columns:
            qs = qs.select_related(*self.select_related_columns)
        return qs


class RuleAdmin(SelectRelatedAdmin):
    search_fields = (
        "chain__name",
        "target__name",
        "src__host",
        "src__name",
        "dst__host",
        "dst__name",
        "description",
    )
    list_filter = ("chain__name", "target__name")
    list_filter_select_related = ("chain__tbl", "target__tbl")
    select_related_columns = (
        "chain__tbl",
        "if_in",
        "if_out",
        "proto",
        "src",
        "sport",
        "dst",
        "dport",
        "target__tbl",
        "created_for",
    )

    def get_list_display(self, request):
        return ["id"] + self.get_fields(request)


for model_name, model in list(app.models.items()):
    if (
        not model_name.endswith("base")
        and not model_name.endswith("log")
        and model_name not in ["rule"]
    ):
        admin.site.register(model, DynamicColumnAdmin)

admin.site.register(Rule, RuleAdmin)
