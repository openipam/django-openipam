from rest_framework import filters as lib_filters
from rest_framework.compat import coreschema
from django.template import loader

class FieldSearchFilterBackend(lib_filters.BaseFilterBackend):
    """Filter that allows for multiple fields to be searched individually."""
    
    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset.
        """
        search_fields = getattr(view, 'search_fields', None)
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
        if not getattr(view, 'search_fields', None):
            return ''
        
        search_fields = [field[1] for field in getattr(view, 'search_fields', None)]
        context = {
            'params': { field: request.query_params.get(field, "") for field in search_fields}
        }
        template = loader.get_template('api_v2/filters/field_search.html')
        return template.render(context)
        
    def get_schema_fields(self, view):
        """
        One search field per field.
        """
        search_fields = getattr(view, 'search_fields', None)
        fields = []
        for field in search_fields:
            fields.append(coreschema.String(field[1], description=field[0]))
        return fields