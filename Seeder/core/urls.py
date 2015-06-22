import views

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^api$', views.ApiPage.as_view(), name='api'),
    url(r'^profile$', views.UserProfileEdit.as_view(), name='user_edit'),
    url(r'^lang/(?P<code>\w+)', views.ChangeLanguage.as_view(),
        name='change_language'),
)
