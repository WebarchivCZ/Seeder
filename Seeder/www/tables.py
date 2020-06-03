from . import models
import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _

from core.tables import AbsoluteURLColumn, NaturalDatetimeColumn


class NewsTable(tables.Table):
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()
    title = AbsoluteURLColumn(
        accessor='__str__',
        verbose_name=_('title')
    )


    class Meta:
        model = models.NewsObject
        fields = ('title', )
        attrs = {
            'class': 'table table-striped table-hover'
        }
        order_by = '-created'


