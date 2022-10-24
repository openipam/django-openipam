from django.views.generic.base import RedirectView
from django.urls import path

from openipam.user import views

app_name = "users"

urlpatterns = [
    path("manager/", views.UserManagerView.as_view(), name="user_manager"),
    path("manager/data/", views.UserManagerJson.as_view(), name="json_hosts"),
    path("manager/user/<int:pk>/", views.user_detail, name="user_detail"),
    path("manager/groups/<int:pk>", views.user_groups, name="user_groups"),
    path(
        "manager/permissions/<int:pk>/",
        views.user_permissions,
        name="user_permissions",
    ),
    path(
        "user/",
        RedirectView.as_view(pattern_name="user_manager"),
        name="user_manager_redirect",
    ),
]
