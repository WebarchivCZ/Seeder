import views
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', views.ListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/create$', views.Create.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/detail$', views.Detail.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/edit$', views.Edit.as_view(), name='edit'),
    url(r'^(?P<pk>\d+)/history$', views.History.as_view(), name='history'),
)
