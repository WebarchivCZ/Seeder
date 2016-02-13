from django.db import models
from django.utils.translation import ugettext_lazy as _


class Blacklist(models.Model):
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
        (TYPE_VISIBILITY, _('Visibility blacklist')),
    )

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
        urls_parsed = map(str.splitlines, blacklist_urls)
        # following line will likely fuck me up cause it is mutable
        return reduce(list.extend, urls_parsed)
