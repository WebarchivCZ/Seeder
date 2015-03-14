from django_pg import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from . import constants


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_changed = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('created', )


class Publisher(BaseModel):
    """
        Publisher of the Source(s), Publisher can have multiple contacts.
    """
    name = models.CharField(_('Name'), max_length=64)
    contacts = models.ArrayField(of=models.CharField())

    class Meta:
        verbose_name = _('Publisher')
        verbose_name_plural = _('Publishers')

    def __unicode__(self):
        return self.name


class Source(BaseModel):
    """
        Source in the context of this project means an information source that
        is going to be downloaded. This usually means website. ``seeds`` field
        represent individual urls. In most of the cases there will be one seed
        which will be equal to ``base_url``.
    """
    created_by = models.ForeignKey(User, related_name='created_by')
    owner = models.ForeignKey(User, verbose_name=_('Curator'))
    name = models.CharField(_('Name'), max_length=64)
    comment = models.TextField(_('Comment'), blank=True)
    base_url = models.URLField()
    web_proposal = models.BooleanField(_('Proposed by visitor'), default=False)
    publisher = models.ForeignKey(verbose_name=_('Publisher'), to=Publisher)
    special_contact = models.CharField(blank=True, max_length=64)

    state = models.CharField(
        verbose_name=_('State'),
        max_length=3,
        choices=constants.SOURCE_STATES)
    conspectus = models.CharField(
        verbose_name=_('Conspectus'),
        choices=constants.CONSPECTUS_CHOICES,
        blank=True,
        max_length=3)
    sub_conspectus = models.CharField(
        verbose_name=_('Sub conspectus'),
        choices=constants.SUB_CONSPECTUS_CHOICES,
        blank=True,
        max_length=3)

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')

    def __unicode__(self):
        return self.name


class Seed(BaseModel):
    """
    Seed is individual url in source
    """
    url = models.URLField(unique=True)
    state = models.CharField(choices=constants.SEED_STATES,
                             default=constants.SEED_STATE_INCLUDE,
                             max_length=3)
    source = models.ForeignKey(Source)
    redirect = models.BooleanField(_('Redirect on seed'), default=False)
    robots = models.BooleanField(_('Robots.txt active'), default=False)
    comment = models.TextField(_('Comment'), blank=True)

    from_time = models.DateTimeField(verbose_name=_('From'), blank=True)
    to_time = models.DateTimeField(verbose_name=_('To'), blank=True)

    class Meta:
        verbose_name = _('Seed')
        verbose_name_plural = _('Seeds')

    def __unicode__(self):
        return self.url


class VotingRound(BaseModel):
    """
        Voting round about source.
    """

    date_ended = models.DateTimeField(_('End of the election'))
    ended_by = models.ForeignKey(User)
    source = models.ForeignKey(Source)
    result = models.CharField(_('Result of the election'),
                              max_length=3,
                              default=constants.VOTING_WAIT,
                              choices=constants.VOTING_RESULT_CHOICES)

    class Meta:
        verbose_name = _('Election')
        verbose_name_plural = _('Elections')

    def __unicode__(self):
        return u'Election: {0}'.format(self.source)

class Vote(BaseModel):
    """
        Individual vote in voting round
    """
    casted_by = models.ForeignKey(User)
    comment = models.TextField(_('Comment'))
    round = models.ForeignKey(verbose_name=_('Round'), to=VotingRound)
    vote = models.CharField(_('Vote'),
                              max_length=3,
                              choices=constants.VOTE_CHOICES)

