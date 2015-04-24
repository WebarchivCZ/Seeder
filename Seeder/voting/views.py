import models
import constants

from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin

from core.utils import LoginMixin, ActionView
from class_based_comments.views import CommentViewGeneric


class VotingDetail(LoginMixin, DetailView, CommentViewGeneric):
    template_name = 'voting_round.html'
    view_name = 'voting'
    model = models.VotingRound
    context_object_name = 'voting_round'


class CastVote(LoginMixin, SingleObjectMixin, ActionView):
    """
    View for casting votes
    """
    model = models.VotingRound
    allowed_actions = constants.VOTES

    def process_action(self, action):
        vote, created = models.Vote.objects.get_or_create(
            author=self.request.user,
            voting_round=self.get_object(),
            defaults={'vote': action})
        if not created and vote.vote != action:
            vote.vote = action
            vote.save()

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_fail_url(self):
        return self.get_object().get_absolute_url()
