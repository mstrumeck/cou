from django.conf.urls import url
from . import views

urlpatterns = [
    url("^list_of_maps/$", views.list_of_maps, name="list_of_maps"),
    url("^list_of_maps/create_new_map/$", views.create_new_map, name="create_new_map"),
    url("^list_of_maps/show_map/(?P<map_id>\d+)$", views.show_map, name="show_map"),
]
