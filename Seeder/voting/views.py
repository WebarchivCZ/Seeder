from . import models
from . import constants
from . import forms

from datetime import datetime, timedelta

from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.http.response import HttpResponseRedirect

from comments.views import CommentViewGeneric
from source.models import Source
from core.generic_views import (
    LoginMixin,
    ActionView,
    ObjectMixinFixed,
    MessageView
)


class VotingView(LoginMixin):
    view_name = 'sources'
    model = models.VotingRound

    def get_queryset(self):
        return super().get_queryset().exclude(source__active=False)


class Create(VotingView, DetailView, MessageView):
    model = Source

    def post(self, request, *args, **kwargs):
        open_rounds = models.VotingRound.objects.filter(
            source=self.get_object(), state=constants.VOTE_INITIAL
        )
        if open_rounds.exists():
            voting_round = open_rounds.first()
            self.add_message(
                _('Open round already exists. Round not created.')
            )
        else:
            voting_round = models.VotingRound(source=self.get_object())
            voting_round.save()
        return HttpResponseRedirect(voting_round.get_absolute_url())


class VotingDetail(VotingView, DetailView, CommentViewGeneric):
    template_name = 'voting_round.html'
    context_object_name = 'voting_round'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_manage'] = self.get_object().can_manage(self.request.user)
        return context


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


class Postpone(VotingView, ObjectMixinFixed, FormView):
    form_class = forms.PostponeForm
    template_name = 'edit_form.html'
    title = _('Postpone voting')
    view_name = 'voting'

    def form_valid(self, form):
        voting_round = self.get_object()
        postpone_months = form.cleaned_data['postpone_months']
        delta = timedelta(days=postpone_months * 30)  # yeah I know.

        voting_round.state = constants.VOTE_WAIT
        voting_round.resolved_by = self.request.user
        voting_round.date_resolved = timezone.now()
        voting_round.postponed_until = datetime.today() + delta
        voting_round.save()
        return HttpResponseRedirect(voting_round.get_absolute_url())


class Resolve(LoginMixin, SingleObjectMixin, ActionView):
    """
    View for resolving the round
    """
    model = models.VotingRound
    allowed_actions = constants.VOTE_DICT.keys()

    def check_permissions(self, user):
        return self.get_object().can_manage(user)

    def process_action(self, action):
        if not self.action == constants.VOTE_WAIT:
            voting_round = self.get_object()
            voting_round.state = action
            voting_round.resolved_by = self.request.user
            voting_round.date_resolved = timezone.now()
            voting_round.save()

    def get_success_url(self):
        if self.action == constants.VOTE_WAIT:
            return reverse_lazy('voting:postpone', kwargs={
                'pk': self.get_object().pk})
        return self.get_object().get_absolute_url()

    def get_fail_url(self):
        return self.get_object().get_absolute_url()
