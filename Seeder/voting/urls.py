import views

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^detail/(?P<pk>\d+)$', views.VotingDetail.as_view(), name='detail'),
    url(r'^detail/(?P<pk>\d+)/(?P<action>\w+)$', views.CastVote.as_view(),
        name='cast'),
)
