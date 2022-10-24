from django.conf.urls import include
from django.contrib.auth.views import password_change_done
from django.views.generic import TemplateView
from django.urls import path

from openipam.core import views


"""
 HEY LOGAN,

 WHEN WE START CONVERTING VIEWS AND ADDING NEW MODELS;
 THE `password_change_done` IMPORT, WILL NEED TO CHANGE
 TO A CLASS BASED VIEW

 P.S. SANTA IS GOOD.

 BEST,
 PARKER
"""

urlpatterns = [
    path("", views.index, name="index"),
    # Accounts URLs
    # url(r'^accounts/login/$', login, name='auth_login'),
    # url(r'^accounts/password/reset/$', password_reset),
    # url(r'^accounts/logout/$', logout, name='auth_logout'),
    # url(r'^accounts/profile/$', 'profile', name='profile'),
    # API
    path("api/", include("openipam.api.urls")),
    # Hosts
    path("hosts/", include("openipam.hosts.urls")),
    # DNS
    path("dns/", include("openipam.dns.urls")),
    # User
    path("user/", include("openipam.user.urls")),
    # USU Reports and Tools
    path("reports/", include("openipam.report.urls")),
    # CAS Login
    # url(r"^cas/login$", cas_login, name="cas_ng_login"),
    # url(r"^cas/logout$", cas_logout, name="cas_ng_logout"),
    # url(r'^cas/callback$', callback, name='cas_ng_proxy_callback'),
    # Duo Auth
    path("duo/auth", views.duo_auth, name="duo_auth"),
    # Account URLS
    path("login/i/", views.login, {"internal": True}, name="internal_login"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, {"next_page": "login"}, name="logout"),
    path("mimic/", views.mimic, name="mimic"),
    path("profile/", views.profile, name="profile"),
    path(
        "password/forgot/",
        TemplateView.as_view(template_name="core/password_forgot.html"),
        name="password_forgot",
    ),
    path("password/change/", views.password_change, name="password_change"),
    path("password/change/done/", password_change_done, name="password_change_done"),
    # These are disabled as in favor of admins changing static account passwords for the user for now.
    # url(r'^password/reset/$', password_reset, name='password_reset'),
    # url(r'^password/reset/done/$', password_reset_done, name='password_reset_done'),
    # url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     password_reset_confirm, name='password_reset_confirm'),
    # url(r'^password/reset/complete/$', password_reset_complete, name='password_reset_complete'),
    path(
        "request/complete/",
        TemplateView.as_view(template_name="core/featurerequest_form.html"),
        {"is_complete": True},
        name="feature_request_complete",
    ),
    path("request/", views.FeatureRequestView.as_view(), name="feature_request"),
]
