from django.urls import path, re_path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeDoneView
from django.views.generic import TemplateView

from openipam.core import views
from openipam.user.forms import IPAMAuthenticationForm

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    # Duo Auth
    path("duo/auth/", views.duo_auth, name="duo_auth"),
    # Account URLS
    path(
        "login/i/",
        LoginView.as_view(form_class=IPAMAuthenticationForm),
        {"internal": True},
        name="internal_login",
    ),
    path("login/", LoginView.as_view(form_class=IPAMAuthenticationForm), name="login"),
    path("logout/", LogoutView.as_view(), {"next_page": "login"}, name="logout"),
    path("mimic/", views.mimic, name="mimic"),
    path("profile/", views.profile, name="profile"),
    path("add_bookmark/", views.add_bookmark, name="menu_add_bookmark"),
    re_path(
        r"^edit_bookmark/(?P<id>.+)/$", views.edit_bookmark, name="menu_edit_bookmark"
    ),
    re_path(
        r"^remove_bookmark/(?P<id>.+)/$",
        views.remove_bookmark,
        name="menu_remove_bookmark",
    ),
    path(
        "password/forgot/",
        TemplateView.as_view(template_name="core/password_forgot.html"),
        name="password_forgot",
    ),
    path(
        "password/change/",
        views.IPAMPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password/change/done/",
        PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "request/complete/",
        TemplateView.as_view(template_name="core/featurerequest_form.html"),
        {"is_complete": True},
        name="feature_request_complete",
    ),
    path("request/", views.FeatureRequestView.as_view(), name="feature_request"),
]
