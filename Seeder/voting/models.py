import constants

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_fsm import FSMField, transition

from core.models import BaseModel
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
        positive_votes, negative_votes, overall = self.get_score_tuple()
        score = u'{vote_sum}/{overall} | +{positive} | -{negative}'.format(
            vote_sum=sum((positive_votes, negative_votes)),
            overall=overall, positive=positive_votes, negative=negative_votes)

        return '{score}: {state}'.format(score=score,
                                         state=self.get_state_display())

    def get_score_tuple(self):
        """
        Aggregation function that returns tuple with score parts
        """
        positive_votes = 6
        negative_votes = 3
        neutral_votes = 5
        overall = positive_votes + negative_votes + neutral_votes
        return positive_votes, negative_votes, overall

    def get_btn_class(self):
        """
            Returns bootstrap btn class
        """
        return constants.VOTING_STATES_TO_COLOURS[self.state]


class Vote(BaseModel):
    """
        Individual vote in voting round
    """
    casted_by = models.ForeignKey(User)
    comment = models.TextField(_('Comment'), blank=True)
    round = models.ForeignKey(verbose_name=_('Round'), to=VotingRound)
    vote = models.CharField(_('Vote'),
                            max_length=3,
                            choices=constants.VOTE_CHOICES)