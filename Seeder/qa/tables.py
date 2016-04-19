from . import models
import django_tables2 as tables

from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn


class QATable(tables.Table):
    pk = AbsoluteURLColumn(accessor='id')
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()

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
