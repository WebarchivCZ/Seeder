import models
import forms
import tables
import field_filters
import constants

from datetime import datetime, timedelta
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

from core import generic_views
from comments.views import CommentViewGeneric
from source.models import Source


class ContractView(generic_views.LoginMixin):
    view_name = 'contracts'
    model = models.Contract


class Detail(ContractView, DetailView, CommentViewGeneric):
    template_name = 'contract.html'


class Create(generic_views.LoginMixin, FormView, SingleObjectMixin):
    form_class = forms.CreateForm
    template_name = 'add_form.html'
    title = _('Add contract')
    view_name = 'contracts'
    model = Source

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(Create, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        contract = form.save(commit=False)
        contract.source = self.object
        contract.save()


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


class Schedule(ContractView, FormView):
    form_class = forms.ScheduledFormset
    template_name = 'schedule.html'
    title = _('Schedule emails')

    def get_initial(self):
        initial = []
        delay = 0
        for template in constants.NEGOTIATION_TEMPLATES:
            rendered = render_to_string(template, context={
                'user': self.request.user
            })
            date = datetime.now() + timedelta(days=delay)
            delay += constants.NEGOTIATION_DELAY
            initial.append({
                'content': rendered,
                'scheduled_date': date,
            })
        return initial
