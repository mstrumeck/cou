from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^main_view/$', views.main_view, name='main_view'),
    url(r'^turn_calculations/$', views.turn_calculations, name='turn_calculations'),
    url(r'^build/(?P<row>\d+)(?P<col>\d+)/(?P<build_type>[-\w]+)/$', views.build, name='build'),
]