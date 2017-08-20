from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<city_id>\d+)/main_view/$', views.main_view, name='main_view')
]