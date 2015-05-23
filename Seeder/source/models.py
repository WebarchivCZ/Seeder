import constants
import reversion

from datetime import datetime

from django.db import models
from django.db.models.query_utils import Q
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from core.models import BaseModel
from publishers.models import Publisher


@reversion.register(exclude=('last_changed',))
class Source(BaseModel):
    """
        Source in the context of this project means an information source that
        is going to be downloaded. This usually means website. ``seeds`` field
        represent individual urls. In most of the cases there will be one seed
        which will be equal to ``base_url``.
    """
    created_by = models.ForeignKey(User, related_name='sources_created')
    owner = models.ForeignKey(User, verbose_name=_('Curator'))
    name = models.CharField(_('Name'), max_length=64)
    comment = models.TextField(_('Comment'), null=True, blank=True)
    web_proposal = models.BooleanField(_('Proposed by visitor'), default=False)
    publisher = models.ForeignKey(verbose_name=_('Publisher'), to=Publisher,
                                  null=True, blank=True)
    special_contact = models.CharField(null=True, blank=True, max_length=64)
    auto_imported = models.BooleanField(_('Imported from old portal'),
                                        default=False)

    alef_number = models.IntegerField(null=True, blank=True)

    state = models.CharField(
        verbose_name=_('State'),
        max_length=3,
        choices=constants.SOURCE_STATES,
        default=constants.STATE_VOTE)

    frequency = models.IntegerField(
        verbose_name=_('Frequency'),
        choices=constants.SOURCE_FREQUENCY_PER_YEAR)

    conspectus = models.CharField(
        verbose_name=_('Conspectus'),
        choices=constants.CONSPECTUS_CHOICES,
        null=True,
        blank=True,
        max_length=5)
    sub_conspectus = models.CharField(
        verbose_name=_('Sub conspectus'),
        choices=constants.SUB_CONSPECTUS_CHOICES,
        null=True,
        blank=True,
        max_length=5)

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')

        # Extra permission for supervisors to enable them manage Sources that
        # they don't own..
        permissions = (
            ('manage_sources', 'Manage others sources'),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('source:detail', args=[str(self.id)])

    def get_valid_contracts(self):
        """
        Returns contracts linking to this model that are valid and did not
        expire.
        """
        return self.contract_set.filter(Q(valid=True) & Q(
            Q(date_end__gte=datetime.now()) | Q(date_end=None)))


@reversion.register(exclude=('last_changed',))
class Seed(BaseModel):
    """
        Seeds are individual urls in Source.
    """
    url = models.URLField(_('Seed url'))
    state = models.CharField(choices=constants.SEED_STATES,
                             default=constants.SEED_STATE_INCLUDE,
                             max_length=3)
    source = models.ForeignKey(Source)
    redirect = models.BooleanField(_('Redirect on seed'), default=False)
    robots = models.BooleanField(_('Robots.txt active'), default=False)
    comment = models.TextField(_('Comment'), null=True, blank=True)

    from_time = models.DateTimeField(verbose_name=_('From'), null=True,
                                     blank=True)
    to_time = models.DateTimeField(verbose_name=_('To'), null=True, blank=True)

    class Meta:
        verbose_name = _('Seed')
        verbose_name_plural = _('Seeds')

    def __unicode__(self):
        return self.url


@reversion.register(exclude=('last_changed',))
class Contract(BaseModel):
    source = models.ForeignKey(Source)

    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)

    contract_file = models.FileField(null=True, blank=True)
    contract_type = models.CharField(choices=constants.CONTRACT_TYPE_CHOICES,
                                     max_length=12)

    valid = models.BooleanField(default=True)
