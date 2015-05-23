import views

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^add$', views.AddSource.as_view(), name='add'),
    url(r'^detail/(?P<pk>\d+)$', views.SourceDetail.as_view(), name='detail'),
    url(r'^history/(?P<pk>\d+)$', views.History.as_view(), name='history'),
    url(r'^edit/(?P<pk>\d+)$', views.SourceEdit.as_view(), name='edit'),
    url(r'^list$', views.SourceList.as_view(), name='list'),
)
