from itertools import chain

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel
from source.constants import SOURCE_FREQUENCY_PER_YEAR
from source.models import Source, Seed


class Harvest(BaseModel):
    """
        Represents the event of harvesting the sources
    """
    STATE_INITIAL = 0
    STATE_SUCCESS = 1
    STATE_CANCELLED = 2
    STATE_FAILED = 3

    STATES = (
        (STATE_INITIAL, _('Created')),
        (STATE_SUCCESS, _('Succeeded')),
        (STATE_CANCELLED, _('Cancelled')),
        (STATE_FAILED, _('Failed')),
    )

    status = models.IntegerField(
        choices=STATES,
        verbose_name=_('State')
    )

    title = models.CharField(blank=True, max_length=255)

    scheduled_on = models.DateField(
        verbose_name=_('Date of harvest')
    )

    target_frequency = models.IntegerField(
        verbose_name=_('Seeds by frequency'),
        choices=SOURCE_FREQUENCY_PER_YEAR,
        blank=True,
        null=True
    )

    custom_sources = models.ManyToManyField(
        Source,
        verbose_name=_('Included sources'),
        blank=True,
    )

    custom_seeds = models.TextField(
        verbose_name=_('Custom seeds URL'),
        help_text=_('One URL per line'),
        blank=True,
        null=True
    )

    def get_absolute_url(self):
        return '/'

    def get_seeds_by_frequency(self):
        seeds = Seed.archiving.filter(source__frequency=self.target_frequency)
        return list(seeds.values_list('url', flat=True))

    def get_custom_seeds(self):
        return self.custom_seeds.splitlines()

    def get_custom_sources_seeds(self):
        seeds = Seed.archiving.filter(source__harvests=self)
        return list(seeds.values_list('url', flat=True))

    def get_seeds(self):
        """
        :return: list of urls
        """
        return chain(
            self.get_seeds_by_frequency(),
            self.get_custom_seeds(),
            self.get_custom_sources_seeds()
        )
