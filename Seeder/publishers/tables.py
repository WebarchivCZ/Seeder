import models
import django_tables2 as tables

from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn


class PublisherTable(tables.Table):
    name = AbsoluteURLColumn()
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()

    class Meta:
        model = models.Publisher
        fields = ('name', 'website', 'email', 'phone')

        attrs = {
            'class': 'table table-striped table-hover'
        }
