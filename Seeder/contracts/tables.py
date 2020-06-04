import django_tables2 as tables

from . import models
from django.utils.translation import ugettext_lazy as _

from core.tables import AbsoluteURLColumn, NaturalDatetimeColumn


class ContractTable(tables.Table):
    link = AbsoluteURLColumn(
        accessor='__str__',
        verbose_name=_('link')
    )
    publisher = AbsoluteURLColumn(
        accessor='publisher',
        verbose_name=_('publisher')
    )
    created = NaturalDatetimeColumn(verbose_name=_('created'))
    last_changed = NaturalDatetimeColumn(verbose_name=_('last_changed'))

    class Meta:
        model = models.Contract
        fields = ('link', 'publisher', 'state', 'valid_from',
                  'valid_to', 'creative_commons', 'in_communication', 'created',
                  'last_changed')

        attrs = {
            'class': 'table table-striped table-hover'
        }
