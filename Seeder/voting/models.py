import constants

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from reversion import revisions as reversion

from core.models import BaseModel, DatePickerField
from core.utils import percentage
from source.models import Source


@reversion.register(exclude=('last_changed',))
class VotingRound(BaseModel):
    """
        Voting round about source.
    """
    source = models.ForeignKey(Source, on_delete=models.DO_NOTHING)
    resolved_by = models.ForeignKey(User, blank=True, null=True)
    date_resolved = models.DateTimeField(blank=True, null=True)
    postponed_until = DatePickerField(blank=True, null=True)

    state = models.CharField(
        verbose_name=_('State'),
        max_length=10,
        choices=constants.VOTE_STATES,
        default=constants.VOTE_INITIAL)

    class Meta:
        verbose_name = _('Election')
        verbose_name_plural = _('Elections')

    def __unicode__(self):
        return self.get_state_display()

    @property
    def round_open(self):
        return self.state == constants.VOTE_INITIAL

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

    def get_status_bar(self):
        """
        Returns iterable with tuple (color, percentage) of status bar
        representing the votes
        """
        score = self.get_score_dict()
        overall = sum(score.values())
        return [(constants.VOTES[vote]['css'], percentage(value, overall))
                for vote, value in score.items()]

    def get_css_class(self):
        """
        Returns bootstrap btn class
        """
        return constants.VOTES[self.state]['css']

    def get_choices(self):
        """
        Returns dict options of possible vote options that can be performed.
        """
        if not self.round_open:
            return {}
        return constants.VOTE_DICT


@reversion.register(exclude=('last_changed',))
class Vote(BaseModel):
    """
        Individual vote in voting round
    """
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    voting_round = models.ForeignKey(
        verbose_name=_('Round'),
        to=VotingRound,
        on_delete=models.DO_NOTHING)
    vote = models.CharField(
        _('Vote'),
        max_length=10,
        choices=constants.VOTE_CHOICES)

    def __unicode__(self):
        return _('{0} - {1}').format(self.author, self.get_vote_display())

    def get_css_class(self):
        """
            Returns bootstrap status class
        """
        return constants.VOTES[self.vote]['css']
