from django.urls import path
from .views import *

urlpatterns = [
    path('add', AddPublisher.as_view(), name='add'),
    path('<int:pk>/detail', Detail.as_view(), name='detail'),
    path('<int:pk>/edit', Edit.as_view(), name='edit'),
    path('<int:pk>/history', History.as_view(), name='history'),
    path('', ListView.as_view(), name='list'),
    path('<int:pk>/contacts', EditContacts.as_view(), name='edit_contacts'),
    path('autocomplete', PublisherAutocomplete.as_view(), name='autocomplete'),
    path('contact_autocomplete', PublisherContactAutocomplete.as_view(),
         name='contact_autocomplete'),
]
