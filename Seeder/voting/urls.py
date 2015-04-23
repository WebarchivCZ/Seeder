import views

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^voting/(?P<pk>\d+)$', views.VotingDetail.as_view(), name='detail'),
)
