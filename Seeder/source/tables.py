import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _
from core.tables import AbsoluteURLColumn, NaturalDatetimeColumn
from . import models


class SourceTable(tables.Table):
    name = AbsoluteURLColumn(verbose_name=_('Name'))
    publisher = AbsoluteURLColumn(
        verbose_name=_('Publisher'),
        accessor='publisher'
    )
    owner = tables.Column(order_by='owner_id')
    category = tables.Column(order_by='category_id')
    sub_category = tables.Column(order_by='sub_category_id')

    created = NaturalDatetimeColumn(verbose_name=_('Created'))
    last_changed = NaturalDatetimeColumn(verbose_name=_('Last changed'))

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'state', 'publisher', 'category',
                  'sub_category', 'suggested_by', 'dead_source',
                  'created', 'last_changed')
        attrs = {
            'class': 'table table-striped table-hover'
        }
        order_by = '-created'
