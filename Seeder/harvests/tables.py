from . import models
import django_tables2 as tables
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from core.tables import AbsoluteURLColumn, NaturalDatetimeColumn


class ChangeOrderColumn(tables.Column):
    verbose_name = ""

    def header(self):
        return ""

    def render(self, value, *args, **kwargs):
        return render_to_string(
            "ordered_model/admin/order_controls.html",
            {
                "urls": {
                    "up": reverse(
                        "harvests:external_collection_change_order",
                        args=[value, "up"]),
                    "down": reverse(
                        "harvests:external_collection_change_order",
                        args=[value, "down"]),
                    "top": reverse(
                        "harvests:external_collection_change_order",
                        args=[value, "top"]),
                    "bottom": reverse(
                        "harvests:external_collection_change_order",
                        args=[value, "bottom"]),
                },
                "query_string": "",
            },
        )


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


class ExternalTopicCollectionTable(tables.Table):
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()
    title = AbsoluteURLColumn(
        accessor='__str__',
        verbose_name=_('title')
    )
    change_order = ChangeOrderColumn(accessor='pk')

    class Meta:
        model = models.ExternalTopicCollection
        fields = ('order', 'change_order', 'title', 'status')

        attrs = {
            'class': 'table table-striped table-hover'
        }
