import models
import constants

from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.http.response import Http404, HttpResponseRedirect

from core.utils import LoginMixin
from class_based_comments.views import CommentViewGeneric


class VotingDetail(LoginMixin, DetailView, CommentViewGeneric):
    template_name = 'voting_round.html'
    view_name = 'voting'
    model = models.VotingRound
    context_object_name = 'voting_round'


class CastVote(LoginMixin, SingleObjectMixin, View):
    """
    View for casting votes... Be design it is not secure against malicious
    linking.
    """
    model = models.VotingRound

    def get(self, request, **kwargs):
        voting_round = self.get_object()
        action = kwargs['action']
        if action not in constants.VOTES:
            raise Http404()

        # vote = models.Vote(
        #     author=request.user,
        #     round=voting_round,
        #     vote=action)
        # vote.save()

        vote, created = models.Vote.objects.get_or_create(
            author=request.user,
            round=voting_round,
            defaults={'vote': action})
        if not created and vote.vote != action:
            vote.vote = action
            vote.save()

        return HttpResponseRedirect(voting_round.get_absolute_url())
