from django.urls import path
from . import views

app_name = "map_engine"

urlpatterns = [
    path("list_of_maps/", views.list_of_maps, name="list_of_maps"),
    path("list_of_maps/create_new_map/", views.create_new_map, name="create_new_map"),
    path("list_of_maps/show_map/<map_id>/", views.show_map, name="show_map"),
]
