import models
import forms
import tables
import field_filters

from django.views.generic import DetailView
from django.utils.translation import ugettext as _

from core import generic_views
from comments.views import CommentViewGeneric


class ContractView(generic_views.LoginMixin):
    view_name = 'contracts'
    model = models.Contract


class Detail(ContractView, DetailView, CommentViewGeneric):
    template_name = 'contract.html'


class Edit(ContractView, generic_views.EditView):
    form_class = forms.PublisherForm


class History(ContractView, generic_views.HistoryView):
    """
        History of changes to publishers
    """


class ListView(ContractView, generic_views.FilteredListView):
    title = _('Sources')
    table_class = tables.PublisherTable
    filter_class = field_filters.PublisherFilter
