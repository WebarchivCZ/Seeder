import constants

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_fsm import FSMField, transition

from core.models import BaseModel
from core.utils import percentage
from source.models import Source


class VotingRound(BaseModel):
    """
        Voting round about source.
    """

    source = models.ForeignKey(Source)
    ended_by = models.ForeignKey(User, blank=True, null=True)
    date_ended = models.DateTimeField(_('End of the election'),
                                      blank=True, null=True)
    state = FSMField(
        verbose_name=_('State'),
        max_length=3,
        choices=constants.VOTING_STATES,
        default=constants.VOTING_INITIAL,
        protected=True)

    class Meta:
        verbose_name = _('Election')
        verbose_name_plural = _('Elections')

    def __unicode__(self):
        return _('Voting round: {source}').format(source=self.source)

    @property
    def round_open(self):
        return self.state == constants.VOTING_INITIAL

    def get_absolute_url(self):
        return reverse('voting:detail', kwargs={'pk': self.pk})

    def get_score_dict(self):
        """
        Aggregation function that returns tuple with score parts
        """
        # count_list is something like this:
        # [{'vote': 'approve', 'count': 2}, {'vote': 'decline', 'count': 5}]
        count_list = self.vote_set.values('vote').annotate(
            count=models.Count('vote')).distinct().order_by()

        # convert count_list to dict syntax:
        # {'approve': 2, 'decline': 5}
        return {d['vote']: d['count'] for d in count_list}

    def get_score_percents(self):
        score = self.get_score_dict()
        overall = sum(score.values())
        return {label: percentage(value, overall)
                for label, value in score.items()}

    def get_css_class(self):
        """
            Returns bootstrap btn class
        """
        return constants.VOTING_STATES_TO_COLOURS[self.state]


class Vote(BaseModel):
    """
        Individual vote in voting round
    """
    author = models.ForeignKey(User)
    voting_round = models.ForeignKey(verbose_name=_('Round'), to=VotingRound)
    vote = models.CharField(
        _('Vote'),
        max_length=10,
        choices=constants.VOTE_CHOICES)

    def get_css_class(self):
        """
            Returns bootstrap status class
        """
        return constants.VOTE_TO_BOOTSTRAP[self.vote]