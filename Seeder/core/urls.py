from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.LandingView.as_view())
)
