import views

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/detail$', views.VotingDetail.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/vote$', views.CastVote.as_view(), name='cast'),
    url(r'^(?P<pk>\d+)/resolve$', views.Resolve.as_view(), name='resolve'),
    url(r'^(?P<pk>\d+)/postpone$', views.Postpone.as_view(), name='postpone'),
)
