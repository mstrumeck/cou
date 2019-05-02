# from django.conf.urls import url
from django.urls import path

from . import views

app_name = "city_engine"

urlpatterns = [
    path(r"main/", views.main_view, name="main"),
    path(r"main/turn_calculations/", views.turn_calculations, name="turn_calculations"),
    path(
        r"build/<row>/<col>/<build_type>/",
        views.build,
    ),
    path(
        r"build_resident/<row>/<col>/<max_population>/",
        views.build_resident,
    ),
    path(r"main/resources/", views.resources, name="resources"),
]
