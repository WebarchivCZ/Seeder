import views

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^detail/(?P<pk>\d+)$', views.VotingDetail.as_view(), name='detail'),
    url(r'^vote/(?P<pk>\d+)$', views.CastVote.as_view(), name='cast'),
    url(r'^resolve/(?P<pk>\d+)$', views.Resolve.as_view(), name='resolve'),
)
