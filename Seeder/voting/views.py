from django.http.response import HttpResponseRedirect
import models
import constants
import forms

from datetime import datetime, timedelta

from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.views.generic import DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from urljects import U, URLView, pk

from core.generic_views import LoginMixin, ActionView, ObjectMixinFixed
from comments.views import CommentViewGeneric


class VotingView(LoginMixin, URLView):
    view_name = 'sources'
    model = models.VotingRound


class VotingDetail(VotingView, DetailView, CommentViewGeneric):
    template_name = 'voting_round.html'
    context_object_name = 'voting_round'

    url = U / pk / 'detail'
    url_name = 'detail'


class CastVote(LoginMixin, SingleObjectMixin, ActionView, URLView):
    """
    View for casting votes
    """
    model = models.VotingRound
    allowed_actions = constants.VOTE_DICT.keys()

    url = U / pk / 'vote'
    url_name = 'cast'

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


class Postpone(VotingView, ObjectMixinFixed, FormView, URLView):
    form_class = forms.PostponeForm
    template_name = 'edit_form.html'
    title = _('Postpone voting')
    view_name = 'voting'

    url = U / pk / 'postpone'
    url_name = 'postpone'

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


class Resolve(LoginMixin, SingleObjectMixin, ActionView, URLView):
    """
    View for resolving the round
    """
    model = models.VotingRound
    allowed_actions = constants.VOTE_DICT.keys()
    permission = 'sources.manage_sources'

    url = U / pk / 'resolve'
    url_name = 'resolve'

    def check_permissions(self, user):
        manager = super(Resolve, self).check_permissions(user)
        return manager or self.get_object().source.owner == user

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
