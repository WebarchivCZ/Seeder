from . import models
import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _

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


class TopicCollectionTable(tables.Table):
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()
    title = AbsoluteURLColumn(
        accessor='__str__',
        verbose_name=_('title')
    )


    class Meta:
        model = models.TopicCollection
        fields = ('title', 'status')

        attrs = {
            'class': 'table table-striped table-hover'
        }


