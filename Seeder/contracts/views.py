import models
import forms
import tables
import field_filters
import constants

from datetime import timedelta, date

from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from urljects import U, URLView, pk

from comments.views import CommentViewGeneric
from source.models import Source
from core.generic_views import (ObjectMixinFixed, LoginMixin, EditView,
                                HistoryView, FilteredListView)


class ContractView(LoginMixin):
    view_name = 'contracts'
    model = models.Contract


class Detail(ContractView, DetailView, CommentViewGeneric, URLView):
    template_name = 'contract.html'

    url = U / pk / 'detail'
    url_name = 'detail'


class Create(LoginMixin, FormView, ObjectMixinFixed, URLView):
    """
    Create contract based on existing source
    """
    form_class = forms.ContractForm
    template_name = 'add_form.html'
    title = _('Add contract')
    view_name = 'contracts'
    model = Source

    url = U / pk / 'create'
    url_name = 'create'

    def form_valid(self, form):
        contract = form.save(commit=False)
        contract.publisher = self.object.publisher
        contract.save()
        contract.sources.add(self.object)
        return HttpResponseRedirect(contract.get_absolute_url())


class Assign(LoginMixin, FormView, ObjectMixinFixed, URLView):
    """
    Assign existing contract to source
    """
    form_class = forms.AssignForm
    template_name = 'add_form.html'
    title = _('Assign contract')
    view_name = 'contracts'
    model = Source

    url = U / pk / 'assign'
    url_name = 'assign'

    def get_form(self, form_class=None):
        form = super(Assign, self).get_form(form_class)
        contract = form.fields['contract']
        contracts = models.Contract.objects.filter(
            publisher=self.get_object().publisher)
        contract.queryset = contracts
        return form

    def form_valid(self, form):
        contract = form.cleaned_data['contract']
        contract.sources.add(self.object)
        return HttpResponseRedirect(contract.get_absolute_url())


class Edit(ContractView, EditView, URLView):
    form_class = forms.ContractForm

    url = U / pk / 'edit'
    url_name = 'edit'

    def form_valid(self, form):
        if (self.get_object().state == constants.CONTRACT_STATE_NEGOTIATION and
                form.cleaned_data['state'] == constants.CONTRACT_STATE_VALID):
            contract = form.save(commit=False)
            contract.contract_number = models.Contract.new_contract_number()
            contract.save()
            self.add_message(_('Contract number assigned.'), messages.SUCCESS)
            self.add_message(_('Changes saved.'), messages.SUCCESS)
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        else:
            return super(Edit, self).form_valid(form)


class History(ContractView, HistoryView, URLView):
    """
        History of changes to contracts
    """

    url = U / pk / 'history'
    url_name = 'history'


class ListView(ContractView, FilteredListView, URLView):
    title = _('Contracts')
    table_class = tables.ContractTable
    filter_class = field_filters.ContractFilter

    url = U
    url_name = 'list'


class Schedule(ContractView, FormView, ObjectMixinFixed, URLView):
    template_name = 'schedule.html'
    title = _('Schedule emails')

    url = U / pk / 'schedule'
    url_name = 'schedule'

    def get_context_data(self, **kwargs):
        context = super(Schedule, self).get_context_data(**kwargs)
        context['source'] = self.object.source
        return context
    
    def get_emails(self):
        return self.object.emailnegotiation_set.all()

    def get_form_class(self):
        extra = (0 if self.get_emails()
                 else len(constants.NEGOTIATION_TEMPLATES))

        return modelformset_factory(
            models.EmailNegotiation,
            fields=('scheduled_date', 'title', 'content'),
            extra=extra, can_delete=True)

    def get_form_kwargs(self):
        kwargs = super(Schedule, self).get_form_kwargs()
        kwargs['queryset'] = self.get_emails()
        return kwargs

    def get_initial(self):
        initial = []
        delay = 0
        today = date.today()
        for template in constants.NEGOTIATION_TEMPLATES:
            rendered = render_to_string(template, context={
                'source': self.object.source,
                'seeds': self.object.source.seed_set.all(),
                'user': self.request.user,
                'today': today,
            })
            scheduled_date = today + timedelta(days=delay)
            delay += constants.NEGOTIATION_DELAY
            initial.append({
                'content': rendered,
                'title': constants.EMAILS_TITLE,
                'scheduled_date': scheduled_date,
            })
        return initial

    def form_valid(self, form):
        for email in form.save(commit=False):
            email.contract = self.object
            email.save()

        for obj in form.deleted_objects:
            obj.delete()

        return HttpResponseRedirect(self.object.get_absolute_url())
