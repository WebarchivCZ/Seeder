import django_tables2 as tables

from django.utils.translation import ugettext_lazy as _
from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn
from . import models


class PublisherTable(tables.Table):
    name = AbsoluteURLColumn(verbose_name=_('Name'))
    created = NaturalDatetimeColumn(verbose_name=_('Created'))
    last_changed = NaturalDatetimeColumn(verbose_name=_('Last changed'))

    class Meta:
        model = models.Publisher
        fields = ('name', )
        attrs = {
            'class': 'table table-striped table-hover'
        }
        order_by = '-created'
