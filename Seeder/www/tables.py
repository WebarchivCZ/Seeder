from . import models
import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from core.tables import AbsoluteURLColumn, NaturalDatetimeColumn


class NewsTable(tables.Table):
    created = NaturalDatetimeColumn()
    last_changed = NaturalDatetimeColumn()
    title = AbsoluteURLColumn(
        accessor='__str__',
        verbose_name=_('title')
    )

    class Meta:
        model = models.NewsObject
        fields = ('title', )
        attrs = {
            'class': 'table table-striped table-hover'
        }
        order_by = '-created'


class ExtinctWebsitesTable(tables.Table):
    def render_url(self, value, record):
        return format_html(
            f"<a href='{record.wayback_url}' target='_blank'>{value}</a>")

    def render_date_extinct(self, value):
        return f"{value:%d.%m.%Y}" if value else "—"

    def render_date_monitoring_start(self, value):
        return f"{value:%d.%m.%Y}" if value else "—"

    def render_status_metadata_match(self, value):
        if value == 0:
            return "✖"
        return value

    class Meta:
        model = models.ExtinctWebsite
        fields = (
            "url",
            "date_extinct",
            "status_code",
            "date_monitoring_start",
            "status_metadata_match",
        )
        attrs = {
            'class': 'table table-sm table-striped table-hover'
        }
        order_by = ("id",)
        # template_name = "django_tables2/bootstrap-responsive.html"
