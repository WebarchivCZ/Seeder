# pylint: disable=W0613

import django_filters

from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django_tables2.columns.linkcolumn import BaseLinkColumn
from django_tables2.columns.base import Column


def merge_dicts(x, y):
    """
    Given two dicts, merge them into a new dict as a shallow copy.
    """
    z = x.copy()
    z.update(y)
    return z


def percentage(part, whole):
    """
    Simple utility for calculating percentages
    """
    return 100 * float(part) / float(whole)


def dict_diff(first, second):
    """
    >>> dict_diff({'a':'b', 'c':1}, {'a':'c', 'c':1})
    {'a': {'original':'b', 'changed': 'c'}

    :type first: dict
    :type second: dict
    :rtype dict
    """
    diff = {}
    keys = set(first.keys() + second.keys())
    for key in keys:
        first_value = first.get(key)
        second_value = second.get(key)
        if first_value != second_value:
            diff[key] = {
                'original': first_value,
                'changed': second_value
            }
    return diff


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
        if isinstance(value, models.Model):
            return self.render_link(uri=value.get_absolute_url(), text=value)
        else:
            return self.render_link(uri=record.get_absolute_url(), text=value)


class NaturalDatetimeColumn(Column):
    """
        Django tables2 column with human date times
    """

    def render(self, value):
        return naturaltime(value)


class EmptyFilter(django_filters.FilterSet):
    """
        Filter that filters based upon icontains lookup and allows empty choice
    """
    empty_choice = ('', '---------')
    filter_overrides = {
        models.CharField: {
            'filter_class': django_filters.CharFilter,
            'extra': lambda f: {
                'lookup_type': 'icontains',
            }
        }
    }

    def __init__(self, *args, **kwargs):
        # pylint: disable=E1002
        super(EmptyFilter, self).__init__(*args, **kwargs)

        # add empty choice to all choice fields:
        is_choice = lambda f: isinstance(self.filters[f],
                                         django_filters.ChoiceFilter)
        choices = filter(is_choice, self.filters)

        for field_name in choices:
            extended_choices = ((self.empty_choice,) +
                                self.filters[field_name].extra['choices'])
            self.filters[field_name].extra['choices'] = extended_choices


def show_toolbar(request):
    return not request.is_ajax() and not request.user.is_anonymous()
