from django.db import models
from django.contrib.auth.models import User

from core.models import BaseModel
from source.constants import SOURCE_FREQUENCY_PER_YEAR
from source_lists.models import HarvestList


class Harvest(BaseModel):
    """
        Represents the event of harvesting the sources
    """
    responsible_curator = models.ForeignKey(User)

    target_frequency = models.CharField(
        choices=SOURCE_FREQUENCY_PER_YEAR,
        blank=True,
        null=True
    )

    target_list = models.OneToOneField(
        HarvestList,
        null=True,
        blank=True
    )
