from django.conf.urls import url
from django.views.generic.base import RedirectView

from openipam.user import views

urlpatterns = [
    url(r'^user/$', RedirectView.as_view(pattern_name='user_manager'), name='user_manager_redirect'),
    url(r'^manager/$', views.UserManagerView.as_view(), name='user_manager'),
    url(r'^manager/user/(?P<pk>\d+)$', views.user_detail, name='user_detail'),
    url(r'^manager/data/$', views.UserManagerJson.as_view(), name='json_hosts'),
    url(r'^manager/groups/(?P<pk>\d+)$', views.user_groups, name='user_groups'),
    url(r'^manager/permissions/(?P<pk>\d+)$', views.user_permissions, name='user_permissions'),
]
