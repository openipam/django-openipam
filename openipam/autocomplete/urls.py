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
        views.IPAMSearchAutoComplete.for_hosts().as_view(),
        name="ipam_autocomplete",
    ),
]
