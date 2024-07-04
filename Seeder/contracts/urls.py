from django.urls import path
from .views import *

urlpatterns = [
    path('<int:pk>/detail', Detail.as_view(), name='detail'),
    path('autocomplete', ContractAutocomplete.as_view(), name='autocomplete'),
    path('<int:pk>/create', Create.as_view(), name='create'),
    path('<int:pk>/assign', Assign.as_view(), name='assign'),
    path('<int:pk>/edit', Edit.as_view(), name='edit'),
    path('<int:pk>/history', History.as_view(), name='history'),
    path('', ListView.as_view(), name='list'),
    path('<int:pk>/schedule', Schedule.as_view(), name='schedule'),
    path('<int:pk>/delete', DeleteView.as_view(), name='delete'),
]
