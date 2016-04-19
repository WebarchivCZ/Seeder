import django_tables2 as tables

from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn
from . import models


class PublisherTable(tables.Table):
    name = AbsoluteURLColumn()
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()

    class Meta:
        model = models.Publisher
        fields = ('name', )

        attrs = {
            'class': 'table table-striped table-hover'
        }
