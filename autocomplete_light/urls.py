"""
An url to AutocompleteView.

autocomplete_light_autocomplete
    Given a 'autocomplete' argument with the name of the autocomplete, this url
    routes to AutocompleteView.

autocomplete_light_registry
    Renders the autocomplete registry, good for debugging, requires being
    authenticated as superuser.
"""
# from .compat import url, urls
from django.urls import path, re_path
from .views import AutocompleteView, RegistryView


urlpatterns = [
    re_path(
        r"^(?P<autocomplete>[-\w]+)/$",
        AutocompleteView.as_view(),
        name="autocomplete_light_autocomplete",
    ),
    path("", RegistryView.as_view(), name="autocomplete_light_registry"),
]
