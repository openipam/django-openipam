from rest_framework import filters as lib_filters
from rest_framework.compat import coreschema
from django.template import loader
from guardian.shortcuts import get_objects_for_user


class RelatedPermissionFilter(lib_filters.BaseFilterBackend):
    """Filter that only allows users to see objects when they have a permission on a related object.

    The view must define the following attributes:
    - filter_related_field: The field to filter on, e.g. 'user' or 'group'
    - filter_perms: A list of permissions to check for, e.g. ['view_host', 'change_host']

    Additionally, the view may define the following attributes:
    - filter_admin_sees_all: If True, admins will see all objects, regardless of
        whether they have the permissions in filter_owner_perms. Defaults to False.
    - filter_staff_sees_all: If True, staff will see all objects, regardless of
        whether they have the permissions in filter_owner_perms. Defaults to False.
    - filter_perms_any: If True, the user can have any of the permissions in filter_perms.
        If False, the user must have all of the permissions in filter_perms. Defaults to True.
    """

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset.
        """
        if not hasattr(view, "filter_perms") or not hasattr(
            view, "filter_related_field"
        ):
            # this filter does nothing if filter_owner_field is not defined
            print("filter_perms or filter_related_field not defined")
            return queryset
        if hasattr(view, "filter_admin_sees_all") and view.filter_admin_sees_all:
            if request.user.is_ipamadmin:
                print("admin sees all")
                return queryset
        if hasattr(view, "filter_staff_sees_all") and view.filter_staff_sees_all:
            if request.user.is_staff:
                print("staff sees all")
                return queryset

        print("user sees theirs")
        related_model = getattr(
            queryset.model, view.filter_related_field
        ).field.related_model
        related_queryset = get_objects_for_user(
            request.user,
            view.filter_perms,
            related_model.objects.all(),
            any_perm=getattr(view, "filter_perms_any", True),
            with_superuser=False,
        )
        return queryset.filter(**{f"{view.filter_related_field}__in": related_queryset})


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

    def to_html(self, request, _, view):
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
