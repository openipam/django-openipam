from django.urls import path, re_path
from django.views.generic.base import RedirectView

from openipam.user import views

app_name = "user"

urlpatterns = [
    path("user/user/", RedirectView.as_view(pattern_name="user:list")),
    path("users/", views.UserManagerView.as_view(), name="list"),
    re_path(r"^users/(?P<pk>\d+)$", views.user_detail, name="detail"),
    path("users/data/", views.UserManagerJson.as_view(), name="json"),
    re_path(r"^groups/(?P<pk>\d+)$", views.user_groups, name="groups"),
    re_path(r"^permissions/(?P<pk>\d+)$", views.user_permissions, name="permissions"),
]
