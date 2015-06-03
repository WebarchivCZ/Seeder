import models
import forms
import tables
import field_filters

from django.views.generic import DetailView, CreateView
from django.utils.translation import ugettext as _

from core import generic_views
from comments.views import CommentViewGeneric


class ContractView(generic_views.LoginMixin):
    view_name = 'contracts'
    model = models.Contract


class Detail(ContractView, DetailView, CommentViewGeneric):
    template_name = 'contract.html'


class Create(ContractView, CreateView):
    form_class = forms.CreateForm


class Edit(ContractView, generic_views.EditView):
    form_class = forms.EditForm


class History(ContractView, generic_views.HistoryView):
    """
        History of changes to contracts
    """


class ListView(ContractView, generic_views.FilteredListView):
    title = _('Contracts')
    table_class = tables.ContractTable
    filter_class = field_filters.ContractFilter
