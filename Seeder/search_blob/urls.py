from django.urls import path
from .views import *

urlpatterns = [
    path('search', SearchView.as_view(), name='search'),
    path('', SearchLogView.as_view(), name='list'),
]
