from rest_framework import filters as lib_filters
from rest_framework.compat import coreschema
from django.template import loader


class FieldSearchFilterBackend(lib_filters.BaseFilterBackend):
    """Filter that allows for multiple fields to be searched individually."""

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset.
        """
        search_fields = getattr(view, "search_fields", None)
        filters = {
            f"{field[0]}__icontains": request.query_params.get(field[1])
            for field in search_fields
            if request.query_params.get(field[1], "") != ""
        }
        return queryset.filter(**filters)

    def to_html(self, request, queryset, view):
        """
        One search box per field.
        """
        if not getattr(view, "search_fields", None):
            return ""

        search_fields = [field[1] for field in getattr(view, "search_fields", None)]
        context = {
            "params": {
                field: request.query_params.get(field, "") for field in search_fields
            }
        }
        template = loader.get_template("api_v2/filters/field_search.html")
        return template.render(context)

    def get_schema_fields(self, view):
        """
        One search field per field.
        """
        search_fields = getattr(view, "search_fields", None)
        fields = []
        for field in search_fields:
            fields.append(coreschema.String(field[1], description=field[0]))
        return fields


class FieldChoiceFilter(lib_filters.BaseFilterBackend):
    """Filter that allows a field to be filtered by a list of choices."""

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset.
        """
        filter_field = getattr(view, "filter_field", None)
        filter_query_prefix = getattr(view, "filter_query_prefix", filter_field)
        filter_choices = getattr(view, "filter_choices", None)
        if filter_field and filter_choices:
            filter_values = [
                value
                for value in filter_choices
                if request.query_params.get(f"{filter_query_prefix}_{value}", "0")
                == "1"
            ]
            print(filter_values)
            if filter_values:
                return queryset.filter(**{f"{filter_field}__in": filter_values})
        return queryset

    def get_schema_fields(self, view):
        """
        Search field.
        """
        filter_field = getattr(view, "filter_field", None)
        if filter_field:
            return [coreschema.String(filter_field, description=filter_field)]
        return []

    def to_html(self, request, queryset, view):
        """
        Multiple checkboxes.
        """
        filter_field = getattr(view, "filter_field", None)
        filter_choices = getattr(view, "filter_choices", None)
        filter_query_prefix = getattr(view, "filter_query_prefix", filter_field)
        if not filter_field or not filter_choices:
            return ""
        context = {
            "filter_field": filter_field,
            "filter_choices": {
                value: request.query_params.get(f"{filter_query_prefix}_{value}", "0")
                == "1"
                for value in filter_choices
            },
            "filter_query_prefix": filter_query_prefix,
        }
        print(context)
        template = loader.get_template("api_v2/filters/field_choice.html")
        return template.render(context)
