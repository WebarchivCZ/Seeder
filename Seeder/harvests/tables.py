from . import models
import django_tables2 as tables

from core.utils import AbsoluteURLColumn, NaturalDatetimeColumn


class HarvestTable(tables.Table):
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()

    class Meta:
        model = models.Harvest
        fields = ('scheduled_on', 'harvest_type', 'target_frequency')

        attrs = {
            'class': 'table table-striped table-hover'
        }
