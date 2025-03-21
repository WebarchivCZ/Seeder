from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('card/<str:card>', DashboardCard.as_view(), name='card'),
    path('reverse-card/<str:card>', DashboardCardReverse.as_view(),
         name='card_reverse'),
    path('lang/<str:code>', ChangeLanguage.as_view(), name='change_language'),
    path('profile', UserProfileEdit.as_view(), name='user_edit'),
    path('crash_test', CrashTestView.as_view(), name='crash_test'),
    path('dev', DevNotesView.as_view(), name='dev_notes'),
    path('site_configuration', EditSiteConfigurationView.as_view(),
         name='site_configuration'),
    path('toggle-wayback-maintenance', ToggleWaybackMaintenanceView.as_view(),
         name='toggle_wayback_maintenance'),
]
