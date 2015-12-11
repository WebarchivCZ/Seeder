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
    TYPE_REGULAR = 1
    TYPE_THEMED = 2

    HARVEST_TYPES = (
        (TYPE_REGULAR, _('Regular harvest')),
        (TYPE_THEMED, _('Seasonal harvest')),
    )

    scheduled_on = models.DateField()
    harvest_type = models.SmallIntegerField(
        verbose_name=_('Harvest type'),
        choices=HARVEST_TYPES
    )

    target_frequency = models.IntegerField(
        verbose_name=_('Frequency'),
        choices=SOURCE_FREQUENCY_PER_YEAR,
        blank=True,
        null=True
    )

    custom_sources = models.ManyToManyField(
        Source,
        blank=True,
        null=True
    )

    custom_seeds = models.TextField(
        verbose_name=_('Custom seeds URL'),
        help_text=_('One URL per line'),
        blank=True,
        null=True
    )

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
