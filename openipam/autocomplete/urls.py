from django.urls import path

from openipam.autocomplete import views

app_name = "autocomplete"

urlpatterns = [
    path(
        "user-autocomplete/",
        views.UserAutocomplete.as_view(),
        name="user_autocomplete",
    ),
    path(
        "group-autocomplete/",
        views.GroupAutocomplete.as_view(),
        name="group_autocomplete",
    ),
    path(
        "ipam-autocomplete/",
        views.IPAMSearchAutoComplete.for_hosts().enable_word_split().as_view(),
        name="ipam_autocomplete",
    ),
    path(
        "permissions-autocomplete/",
        views.PermissionsAutocomplete.as_view(),
        name="permission_autocomplete",
    ),
    path(
        "contenttype-autocomplete/",
        views.ContentTypeAutocomplete.as_view(),
        name="content_type_autocomplete",
    ),
    path(
        "host-autocomplete/",
        views.HostAutocomplete.as_view(),
        name="host_autocomplete",
    )
]
