import django_tables2 as tables

from django.utils.translation import ugettext_lazy as _
from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn
from . import models


class SourceTable(tables.Table):
    name = AbsoluteURLColumn(verbose_name=_('Name'))
    publisher = AbsoluteURLColumn(
        verbose_name=_('Publisher'),
        accessor='publisher'
    )
    created = NaturalDatetimeColumn(verbose_name=_('Created'))
    last_changed = NaturalDatetimeColumn(verbose_name=_('Last changed'))

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'created', 'last_changed', 'state',
                  'publisher', 'category', 'sub_category', 'suggested_by')
        attrs = {
            'class': 'table table-striped table-hover'
        }
