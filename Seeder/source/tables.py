# pylint: disable=W0613
import models
import django_tables2 as tables

from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn


class SourceTable(tables.Table):
    name = AbsoluteURLColumn()
    publisher = AbsoluteURLColumn(accessor='publisher')
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'created', 'last_changed', 'state',
                  'publisher', 'conspectus', 'sub_conspectus')
        attrs = {
            'class': 'table table-striped table-hover'
        }
