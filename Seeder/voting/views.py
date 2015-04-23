import models

from django.views.generic import DetailView

from core.utils import LoginMixin
from class_based_comments.views import CommentViewGeneric


class VotingDetail(LoginMixin, DetailView, CommentViewGeneric):
    template_name = 'voting_round.html'
    view_name = 'voting'
    model = models.VotingRound
    anonymous = False
