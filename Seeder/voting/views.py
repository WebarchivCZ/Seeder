import models
import constants

from django.contrib import messages
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.utils.translation import ugettext as _

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
    allowed_actions = constants.VOTE_DICT.keys()

    def process_action(self, action):
        vote, created = models.Vote.objects.get_or_create(
            author=self.request.user,
            voting_round=self.get_object(),
            defaults={'vote': action})
        if not created and vote.vote != action:
            self.add_message(_('Vote changed'), messages.SUCCESS)
            vote.vote = action
            vote.save()
        else:
            self.add_message(_('Vote created'), messages.SUCCESS)

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_fail_url(self):
        return self.get_object().get_absolute_url()


class ResolveVote(LoginMixin, SingleObjectMixin, ActionView):
    """
    View for casting votes
    """
    model = models.VotingRound
    allowed_actions = constants.VOTE_DICT.keys()
    permission = 'sources.manage_sources'

    def process_action(self, action):
        pass

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_fail_url(self):
        return self.get_object().get_absolute_url()
