import models
import django_tables2 as tables

from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn


class ContractTable(tables.Table):
    name = AbsoluteURLColumn()
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()

    class Meta:
        model = models.Contract
        fields = ('source', 'state', 'date_start', 'date_end',
                  'contract_type', 'in_communication')

        attrs = {
            'class': 'table table-striped table-hover'
        }
