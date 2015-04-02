import models
import django_tables2 as tables

from django_tables2.columns.linkcolumn import BaseLinkColumn


class AbsoluteURLColumn(BaseLinkColumn):
    """
    Renders models get_absolute_url
    """

    def render(self, value, record, bound_column):
        # if this was created using accessor, value is the thing we want
        if isinstance(value, models.BaseModel):
            return self.render_link(uri=value.get_absolute_url(), text=value)
        else:
            return self.render_link(uri=record.get_absolute_url(), text=value)


class SourceTable(tables.Table):
    name = AbsoluteURLColumn()
    # publisher = AbsoluteURLColumn(accessor='publisher')

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'created', 'last_changed', 'state',
                  'publisher', 'conspectus', 'sub_conspectus')
        attrs = {
            'class': 'table table-striped'
        }