from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.main_page, name='main_page'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'login/$', auth_views.login, name='login'),
    url(r'logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'logout-then-login/$', auth_views.logout_then_login, name='logout_then_login'),
]