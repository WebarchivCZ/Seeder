import models
import forms
import tables
import field_filters

from django.views.generic import DetailView
from django.utils.translation import ugettext as _

from core import generic_views
from comments.views import CommentViewGeneric


class PublisherView(generic_views.LoginMixin):
    view_name = 'publishers'
    model = models.Publisher


class Detail(PublisherView, DetailView, CommentViewGeneric):
    template_name = 'publisher.html'


class Edit(PublisherView, generic_views.EditView):
    form_class = forms.PublisherForm


class History(PublisherView, generic_views.HistoryView):
    """
        History of changes to publishers
    """


class ListView(PublisherView, generic_views.FilteredListView):
    title = _('Sources')
    table_class = tables.PublisherTable
    filter_class = field_filters.PublisherFilter
