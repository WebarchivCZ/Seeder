from django.views import View

from . import models
from . import forms
from . import tables
from . import field_filters
from . import constants

from datetime import timedelta, date
from dal import autocomplete

from django.db.models.functions import Cast
from django.db.models import CharField
from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from comments.views import CommentViewGeneric
from source.models import Source
import source.constants as source_constants
from core.generic_views import (ObjectMixinFixed, LoginMixin, EditView,
                                HistoryView, FilteredListView, MessageView)


class ContractView(LoginMixin):
    view_name = 'contracts'
    model = models.Contract


class Detail(ContractView, DetailView, CommentViewGeneric):
    template_name = 'contract.html'


class ContractAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Contract.objects.none()
        # Annotate as strings so we can use icontains
        qs = models.Contract.objects.all().annotate(
            contract_number_s=Cast("contract_number", output_field=CharField()),
            year_s=Cast("year", output_field=CharField())
        ).order_by("contract_number", "year")
        # Allow searching by "{contract_number} / {year}"
        if self.q:
            q_split = str(self.q or "").replace(" ", "").split("/")
            if len(q_split) == 1:
                qs = qs.filter(contract_number_s__icontains=q_split[0])
            elif len(q_split) == 2:
                qs = qs.filter(contract_number_s__icontains=q_split[0],
                               year_s__icontains=q_split[1])
        return qs


class Create(LoginMixin, FormView, ObjectMixinFixed):
    """
    Create contract based on existing source
    """
    form_class = forms.ContractForm
    template_name = 'add_form.html'
    title = _('Add contract')
    view_name = 'contracts'
    model = Source

    def form_valid(self, form):
        contract = form.save(commit=False)
        contract.publisher = self.object.publisher
        contract.save()

        if contract.is_valid():
            contract.assign_number()

        contract.sources.add(self.object)
        return HttpResponseRedirect(contract.get_absolute_url())


class Assign(LoginMixin, FormView, ObjectMixinFixed):
    """
    Assign existing contract to source
    """
    form_class = forms.AssignForm
    template_name = 'add_form.html'
    title = _('Assign contract')
    view_name = 'contracts'
    model = Source

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        contract = form.fields['contract']
        contracts = models.Contract.objects.filter(
            publisher=self.get_object().publisher
        )
        if contracts.exists():
            contract.queryset = contracts
        else:
            contract.queryset = models.Contract.objects.valid()
        return form

    def form_valid(self, form):
        contract = form.cleaned_data['contract']
        contract.sources.add(self.object)
        # When assigned to a contract, source should be marked as "archiving"
        self.object.state = source_constants.STATE_RUNNING
        self.object.save()
        return HttpResponseRedirect(contract.get_absolute_url())


class Edit(ContractView, EditView):
    form_class = forms.ContractForm

    def form_valid(self, form):
        contract = form.save()
        contract_has_no_number = not contract.contract_number

        if contract_has_no_number and contract.is_valid():
            contract.assign_number()
            self.add_message(_('Contract number assigned.'), messages.SUCCESS)
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        else:
            return super().form_valid(form)


class History(ContractView, HistoryView):
    """
        History of changes to contracts
    """
    pass


class ListView(ContractView, FilteredListView):
    title = _('Contracts')
    table_class = tables.ContractTable
    filterset_class = field_filters.ContractFilter


class Schedule(ContractView, FormView, ObjectMixinFixed):
    template_name = 'schedule.html'
    title = _('Schedule emails')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source'] = self.object.sources.first()
        return context

    def get_emails(self):
        return self.object.emailnegotiation_set.all()

    def get_form_class(self):
        extra = (0 if self.get_emails()
                 else len(constants.NEGOTIATION_TEMPLATES))

        return modelformset_factory(
            models.EmailNegotiation,
            fields=('to_email', 'scheduled_date', 'title', 'content', ),
            extra=extra, can_delete=True
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.get_emails()
        return kwargs

    def get_initial(self):
        initial = []
        delay = 0
        today = date.today()

        source = self.object.sources.first()

        for template in constants.NEGOTIATION_TEMPLATES:
            rendered = render_to_string(template, context={
                'source': source,
                'seeds': source.seed_set.all(),
                'user': self.request.user,
                'today': today,
            })
            scheduled_date = today + timedelta(days=delay)
            delay += constants.NEGOTIATION_DELAY
            initial.append({
                'content': rendered,
                'title': constants.EMAILS_TITLE,
                'scheduled_date': scheduled_date,
                'to_email': source.publisher_contact.email
                if source.publisher_contact else ''
            })
        return initial

    def form_valid(self, form):
        for email in form.save(commit=False):
            email.contract = self.object
            email.save()

        for obj in form.deleted_objects:
            obj.delete()

        return HttpResponseRedirect(self.object.get_absolute_url())


class DeleteView(View, MessageView, ContractView, ObjectMixinFixed):
    def post(self, request, *args, **kwargs):
        contract = self.get_object()
        if not contract.can_delete():
            self.add_message(
                _("Can't delete contract with number"),
                messages.ERROR
            )
            return HttpResponseRedirect(contract.get_absolute_url())

        source_url = contract.sources.first().get_absolute_url()
        contract.delete()
        self.add_message(
            _('Contract deleted.'),
            messages.SUCCESS
        )
        return HttpResponseRedirect(source_url)
