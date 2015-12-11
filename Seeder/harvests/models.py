from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel
from source.constants import SOURCE_FREQUENCY_PER_YEAR
from source.models import Source


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
        verbose_name=('Harvest type'),
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
