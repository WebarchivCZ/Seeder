from django.db import models

from source.models import Source
from core.models import BaseModel


class BaseListModel(BaseModel):
    sources = models.ForeignKey(Source)
    additional_seeds = models.TextField()

    class Meta:
        abstract = True


class BlackList(BaseListModel):
    """
    Model describing various blacklists that can be enabled or disabled
    """
    pass


class HarvestList(BaseListModel):
    """
    This will represent list of sources in Themed harvests
    """
    title = models.CharField(max_length=64)
