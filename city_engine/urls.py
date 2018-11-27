from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^main/$', views.main_view, name='main'),
    url(r'^turn_calculations/$', views.turn_calculations, name='turn_calculations'),
    url(r'^build/(?P<row>\d+)(?P<col>\d+)/(?P<build_type>[-\w]+)/$', views.build, name='build'),
    url(r'^build_resident/(?P<row>\d+)(?P<col>\d+)/(?P<max_population>\d+)/$', views.build_resident, name='build_resident'),
    url(r'^main/resources/$', views.resources_view, name='resources'),
]