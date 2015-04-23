import views
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^p/(?P<pk>\d+)$', views.PublisherDetail.as_view(), name='detail'),
)
