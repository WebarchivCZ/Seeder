import constants

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_fsm import FSMField, transition

from core.models import BaseModel
from source.models import Source


def percentage(part, whole):
    """
    Simple utility for calculating percentages
    """
    return 100 * float(part)/float(whole)


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

    def score_display(self):
        score = self.get_score_dict()
        score = u'{vote_sum}/{overall} | +{positive} | -{negative}'.format(
            vote_sum=score['positive'] - score['negative'],
            overall=score['overall'], positive=score['positive'],
            negative=score['negative'])

        return '{score}: {state}'.format(score=score,
                                         state=self.get_state_display())

    def get_absolute_url(self):
        return reverse('voting:detail', kwargs={'pk': self.pk})

    def get_score_dict(self):
        """
        Aggregation function that returns tuple with score parts
        """
        positive_votes = 6
        negative_votes = 3
        neutral_votes = 5
        overall = positive_votes + negative_votes + neutral_votes
        return {
            'positive': positive_votes,
            'negative': negative_votes,
            'neutral': neutral_votes,
            'overall': overall,
        }

    def get_score_percents(self):
        score = self.get_score_dict()
        overall = score['overall']
        return {
            'positive': percentage(score['positive'], overall),
            'negative': percentage(score['negative'], overall),
            'neutral': percentage(score['neutral'], overall),
        }

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
    round = models.ForeignKey(verbose_name=_('Round'), to=VotingRound)
    vote = models.CharField(
        _('Vote'),
        max_length=10,
        choices=constants.VOTE_CHOICES)

    def get_css_class(self):
        """
            Returns bootstrap status class
        """
        return constants.VOTE_TO_BOOTSTRAP[self.vote]