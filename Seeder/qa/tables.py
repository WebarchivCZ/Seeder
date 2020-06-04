from . import models

import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _
from core.tables import AbsoluteURLColumn, NaturalDatetimeColumn


class QATable(tables.Table):
    pk = AbsoluteURLColumn(accessor='id')
    created = NaturalDatetimeColumn(verbose_name=_('created'))
    last_changed = NaturalDatetimeColumn(verbose_name=_('last_changed'))

    class Meta:
        model = models.QualityAssuranceCheck
        fields = [
            'pk',
            'source',
            'content_changed',
            'technical_quality_changed',
            'source_action',
        ]

        attrs = {
            'class': 'table table-striped table-hover'
        }
