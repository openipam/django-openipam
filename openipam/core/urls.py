from django.conf.urls import url, include
from django.contrib.auth.views import password_change_done
from django.views.generic import TemplateView

from openipam.core import views, auth


urlpatterns = [
    url(r"^$", views.index, name="index"),
    # Accounts URLs
    # url(r'^accounts/login/$', login, name='auth_login'),
    # url(r'^accounts/password/reset/$', password_reset),
    # url(r'^accounts/logout/$', logout, name='auth_logout'),
    # url(r'^accounts/profile/$', 'profile', name='profile'),
    # API
    url(r"^api/", include("openipam.api.urls")),
    # Hosts
    url(r"^hosts/", include("openipam.hosts.urls")),
    # DNS
    url(r"^dns/", include("openipam.dns.urls")),
    # User
    url(r"^user/", include("openipam.user.urls")),
    # USU Reports and Tools
    url(r"^reports/", include("openipam.report.urls")),
    # SAML2 Auth
    url(r"^acs/$", auth.acs, name="acs"),
    # Duo Auth
    url(r"^duo/auth$", views.duo_auth, name="duo_auth"),
    # Account URLS
    url(r"^login/i/$", views.login, {"internal": True}, name="internal_login"),
    url(r"^login/$", views.login, name="login"),
    url(r"^logout/$", views.logout, {"next_page": "login"}, name="logout"),
    url(r"^mimic/$", views.mimic, name="mimic"),
    url(r"^profile/$", views.profile, name="profile"),
    url(
        r"^password/forgot/$",
        TemplateView.as_view(template_name="core/password_forgot.html"),
        name="password_forgot",
    ),
    url(r"^password/change/$", views.password_change, name="password_change"),
    url(r"^password/change/done/$", password_change_done, name="password_change_done"),
    # These are disabled as in favor of admins changing static account passwords for the user for now.
    # url(r'^password/reset/$', password_reset, name='password_reset'),
    # url(r'^password/reset/done/$', password_reset_done, name='password_reset_done'),
    # url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     password_reset_confirm, name='password_reset_confirm'),
    # url(r'^password/reset/complete/$', password_reset_complete, name='password_reset_complete'),
    url(
        r"^request/complete/$",
        TemplateView.as_view(template_name="core/featurerequest_form.html"),
        {"is_complete": True},
        name="feature_request_complete",
    ),
    url(r"^request/$", views.FeatureRequestView.as_view(), name="feature_request"),
]
