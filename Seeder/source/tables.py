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

    # Seeder = show # of seeds ; Export = show URLs joined w/ a comma
    urls = tables.Column(accessor="seed_set.all")

    def value_urls(self, record, value):
        return ",".join(value.values_list("url", flat=True))

    def render_urls(self, record, value):
        return value.count()

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'state', 'publisher', 'category',
                  'sub_category', 'suggested_by', 'dead_source', 
                  'priority_source', 'created', 'last_changed', 'urls')
        attrs = {
            'class': 'table table-striped table-hover'
        }
        order_by = '-created'
