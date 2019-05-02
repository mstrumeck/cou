from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "player"

urlpatterns = [
    path(r"", views.main_page, name="main_page"),
    path(r"signup/", views.signup, name="signup"),
    path(
        r"account_activation_sent/",
        views.account_activation_sent,
        name="account_activation_sent",
    ),
    # url(
    #     r"^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
    #     views.activate,
    #     name="activate",
    # ),
    path(r"login/", auth_views.LoginView, name="login"),
    path(r"logout/", auth_views.LogoutView, {"next_page": "/"}, name="logout"),
    path(r"logout-then-login/", auth_views.logout_then_login, name="logout_then_login"),
]
