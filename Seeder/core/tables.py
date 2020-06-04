from django.db import models
from django_tables2.columns.linkcolumn import BaseLinkColumn
from django_tables2.columns import DateTimeColumn, DateColumn
from django.utils.html import format_html


class AbsoluteURLColumn(BaseLinkColumn):
    """
        Django tables2 column that renders models get_absolute_url
    """

    def render(self, record, table, value, bound_column, **kwargs):
        """
        This is kind of dirty, but django-tables2 uses some weirds tricks.
        (Look at render method of LinkColumn and URLColumn, each has different
        set of arguments!)

        If this was created using accessor, value is the thing we want.
        Otherwise value is the text to display and record is the main model.
        """

        url = (
            value.get_absolute_url() if isinstance(value, models.Model)
            else record.get_absolute_url()
        )
        return self.render_link(
            uri=url, record=record, value=value
        )


class NaturalDatetimeColumn(DateTimeColumn):
    """
        Django tables2 column that renders date with datetime on hover
    """

    def render(self, *args, **kwargs):
        datetime = super().render(*args, **kwargs)
        date = DateColumn().render(*args, **kwargs)

        return format_html(f"<span title='{datetime}'>{date}</span>")
