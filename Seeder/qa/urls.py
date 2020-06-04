from django.urls import path
from .views import *

urlpatterns = [
    path('source/<int:pk>/create', QACreate.as_view(), name='create'),
    path('<int:pk>/edit', QAEdit.as_view(), name='edit'),
    path('<int:pk>/detail', QADetail.as_view(), name='detail'),
    path('', ListView.as_view(), name='list'),
]
