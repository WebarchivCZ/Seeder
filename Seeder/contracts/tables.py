import models
import django_tables2 as tables

from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn


class ContractTable(tables.Table):
    link = AbsoluteURLColumn(accessor='__unicode__')
    publisher = AbsoluteURLColumn(accessor='publisher')
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()

    class Meta:
        model = models.Contract
        fields = ('link', 'publisher', 'state', 'valid_to',
                  'valid_from', 'open_source', 'in_communication', 'created',
                  'last_changed')

        attrs = {
            'class': 'table table-striped table-hover'
        }
