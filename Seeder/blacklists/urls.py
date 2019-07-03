from django.urls import path
from .views import *

urlpatterns = [
    path('', ListView.as_view(), name='list'),
    path('add', AddView.as_view(), name='add'),
    path('<int:pk>/edit', EditView.as_view(), name='edit'),
    path('history/<int:pk>', History.as_view(), name='history'),
    path('dump', BlacklistDump.as_view(), name='dump'),
]
