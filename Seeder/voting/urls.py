from django.urls import path
from .views import *

urlpatterns = [
    path('<int:pk/create', Create.as_view(), name='create'),
    path('<int:pk/detail', VotingDetail.as_view(), name='detail'),
    path('<int:pk/vote', CastVote.as_view(), name='cast'),
    path('<int:pk/postpone', Postpone.as_view(), name='postpone'),
    path('<int:pk/resolve', Resolve.as_view(), name='resolve'),
]
