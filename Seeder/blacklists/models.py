import operator
from functools import reduce

from django.db import models
from django.utils.translation import ugettext_lazy as _
from reversion import revisions

from core.models import BaseModel


@revisions.register
class Blacklist(BaseModel):
    """
    General model for control lists

    There are two types of blacklists
    - blacklist that control Haritrex
    - visibility blacklists that control which pages can be accessed by visitor
    """
    TYPE_HARVEST = 0        # controls what gets harvested
    TYPE_VISIBILITY = 1     # controls what can be seen

    TYPE_CHOICES = (
        (TYPE_HARVEST, _('Haritrex blacklist')),
        (TYPE_VISIBILITY, _('Wayback blacklist')),
    )

    title = models.CharField(verbose_name=_('Title'), max_length=256)

    blacklist_type = models.IntegerField(
        choices=TYPE_CHOICES
    )

    url_list = models.TextField(
        verbose_name=_('List of urls to block')
    )

    class Meta:
        verbose_name = _('Blacklist')
        verbose_name_plural = _('Blacklists')
        ordering = ('id', )

    @classmethod
    def collect_urls_by_type(cls, blacklist_type):
        blacklist_urls = cls.objects.filter(
            blacklist_type=blacklist_type
        ).values_list('url_list', flat=True)
        # blacklist urls is now list of contents
        urls_parsed = map(str.split, blacklist_urls)
        return reduce(operator.add, urls_parsed, [])

    @classmethod
    def last_change(cls):
        agg = Blacklist.objects.all().aggregate(models.Max('last_changed'))
        return agg.get('last_changed__max')

    @classmethod
    def dump(cls):
        blacklist_urls = cls.objects.all().values_list('url_list', flat=True)
        urls_parsed = map(str.split, blacklist_urls)
        # Remove duplicates
        return list(set(reduce(operator.add, urls_parsed, [])))
