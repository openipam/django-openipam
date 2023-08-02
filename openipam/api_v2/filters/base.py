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
    """Filter that allows a field to be filtered by a list of choices.

    The view must define the following attributes:
    - filter_field: The field to filter on, e.g. 'status' or 'user__username'
    - At least one of the following:
        - filter_choices: A list of choices, e.g. ['active', 'inactive'], which must be valid values for filter_field, and valid strings for query parameters.
        - filter_allow_unlisted: A boolean indicating whether to allow values not in filter_choices.

    The filter will look for a query parameter for each choice, e.g. 'status_active=1' or 'status_inactive=1'.
    By default, it will use the value of filter_field as the query parameter prefix, e.g. 'status_active=1'.
    To override this, set filter_query_prefix to the desired prefix, e.g. 'include_active=1'.

    If filter_allow_unlisted is True, the filter will also read any additional query parameters that start with
    the prefix, e.g. 'status_active=1&status_inactive=1&status_pending=1' will return all objects with status
    'active', 'inactive', or 'pending', even if 'pending' is not in filter_choices.

    This filter does nothing if filter_field is not defined, or if there are no matching query parameters in the request.
    """

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset.
        """
        filter_field = getattr(view, "filter_field", None)
        filter_query_prefix = getattr(view, "filter_query_prefix", filter_field)
        filter_choices = getattr(view, "filter_choices", [])
        filter_allow_unlisted = getattr(view, "filter_allow_unlisted", False)
        if filter_allow_unlisted:
            for param in request.query_params.keys():
                if param.startswith(f"{filter_query_prefix}_"):
                    filter_choices.append(param[len(filter_query_prefix) + 1 :])
        if filter_field and filter_choices:
            filter_values = [
                value
                for value in filter_choices
                if request.query_params.get(f"{filter_query_prefix}_{value}", "0")
                == "1"
            ]
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

    def to_html(self, request, _, view):
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
