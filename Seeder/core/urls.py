from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.LandingView.as_view()),
    url(r'^add/$', views.AddSource.as_view(), name='add_source')
)
