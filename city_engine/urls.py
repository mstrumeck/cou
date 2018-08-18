from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^main/$', views.main_view, name='main'),
    url(r'^turn_calculations/$', views.turn_calculations, name='turn_calculations'),
    url(r'^build/(?P<row>\d+)(?P<col>\d+)/(?P<build_type>[-\w]+)/$', views.build, name='build'),
    url(r'^main/resources/$', views.resources_view, name='resources'),
]