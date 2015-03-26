import views

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^add/$', views.AddSource.as_view(), name='add_source')
)
