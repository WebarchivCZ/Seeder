import models
import django_tables2 as tables

from django_tables2.columns.linkcolumn import BaseLinkColumn
from django_tables2.columns.base import Column
from django.contrib.humanize.templatetags.humanize import naturaltime


class AbsoluteURLColumn(BaseLinkColumn):
    """
    Renders models get_absolute_url
    """

    def render(self, record, table, value, bound_column, **kwargs):
        """
        This is kind of dirty, but django-tables2 uses some weirds tricks.
        (Look at render method of LinkColumn and URLColumn, each has different
        set of arguments!)

        If this was created using accessor, value is the thing we want.
        Otherwise value is the text to display and record is the main model.
        """
        if isinstance(value, models.BaseModel):
            return self.render_link(uri=value.get_absolute_url(), text=value)
        else:
            return self.render_link(uri=record.get_absolute_url(), text=value)


class NaturalDatetimeColumn(Column):
    """
    Column with human date times
    """

    def render(self, value):
        return naturaltime(value)


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