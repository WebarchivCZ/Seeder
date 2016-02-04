import forms
import models
import tables
import field_filters

from django.views.generic import DetailView, FormView
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from formtools.wizard.views import SessionWizardView
from datetime import datetime
from urljects import U, URLView, pk

from contracts.models import Contract
from publishers import forms as publisher_forms
from core import generic_views
from comments.views import CommentViewGeneric
from contracts import constants as contract_constants


def show_publisher_create_form(wizard):
    """
        Django form wizard condition
    """
    cleaned_data = wizard.get_cleaned_data_for_step('source') or {}
    return not cleaned_data.get('publisher', False)


def show_publisher_choose_form(wizard):
    """
        Django form wizard condition
    """
    cleaned_data = wizard.get_cleaned_data_for_step('source') or {}
    return cleaned_data.get('publisher', False)


class SourceView(generic_views.LoginMixin):
    view_name = 'sources'
    model = models.Source


class AddSource(generic_views.LoginMixin, SessionWizardView, URLView):
    template_name = 'add_source.html'
    view_name = 'add_source'

    url = U / 'add'
    url_name = 'add'

    form_list = (
        ('source', forms.SourceForm),
        ('choose_publisher', publisher_forms.ContactChoiceForm),
        ('create_publisher', publisher_forms.PublisherForm),
        ('seeds', forms.SeedFormset),
        ('duplicity', forms.DuplicityForm),
    )

    template_names = {
        'seeds': 'add_seeds_static.html',
        'duplicity': 'duplicity_check.html',
    }

    titles = {
        'source': _('Add source'),
        'create_publisher': _('Add publisher'),
        'choose_publisher': _('Choose contact person'),
        'seeds': _('Add seeds'),
        'duplicity': _('Check for duplicities'),
    }

    condition_dict = {
        'create_publisher': show_publisher_create_form,
        'choose_publisher': show_publisher_choose_form
    }

    def get_title(self):
        return self.titles[self.steps.current]

    def get_form(self, step=None, data=None, files=None):
        """
            Dynamically set source form according to user rights
        """
        step = step or self.steps.current
        is_manager = self.request.user.has_perm('core.manage_sources')
        form_class = self.form_list[step]

        if step == 'source' and is_manager:
            form_class = forms.ManagementSourceForm
            form = form_class(prefix=self.get_form_prefix(step, form_class),
                              data=data, files=files)
            owner = form.fields['owner']
            owner.initial = self.request.user
            return form

        elif step == 'choose_publisher':
            publisher = self.get_cleaned_data_for_step('source')['publisher']
            form = form_class(prefix=self.get_form_prefix(step, form_class),
                              data=data, files=files)
            contact = form.fields['contact']
            contact.queryset = publisher.contactperson_set.all()
            contact.initial = contact.queryset[0]
            return form

        return form_class(prefix=self.get_form_prefix(step, form_class),
                          data=data, files=files)

    def get_template_names(self):
        if self.steps.current in self.template_names:
            return self.template_names[self.steps.current]
        return super(AddSource, self).get_template_names()

    def get_duplicities(self):
        """
        Returns queryset with similar records
        """

        source_data = self.get_cleaned_data_for_step('source')
        publisher_data = self.get_cleaned_data_for_step('create_publisher')
        seeds_data = self.get_cleaned_data_for_step('seeds')
        seeds_url = [s.get('url', '') for s in seeds_data]

        filters = (Q(name__icontains=source_data['name']) |
                   Q(seed__url__in=seeds_url))
        if publisher_data:
            filters |= Q(publisher__name__icontains=publisher_data['name'])

        return models.Source.objects.filter(filters).distinct()

    def done(self, form_list, **kwargs):
        form_dict = kwargs['form_dict']
        user = self.request.user
        source_form = form_dict['source']
        publisher_new = form_dict.get('create_publisher', None)
        publisher_choice = form_dict.get('choose_publisher', None)
        seed_formset = form_dict['seeds']
        is_manager = user.has_perm('core.manage_sources')

        source = source_form.save(commit=False)
        source.created_by = user

        if not is_manager or not source.created_by:
            source.owner = user

        if publisher_new:
            source.publisher, source.publisher_contact = publisher_new.save()
        if publisher_choice:
            # this forms has two modes - create new object or choose existing
            contact = publisher_choice.cleaned_data['contact']
            if not contact:
                contact = publisher_choice.save(commit=False)
                contact.publisher = source.publisher
                contact.save()
            source.publisher_contact = contact
        source.save()

        if source_form.cleaned_data['open_license']:
            contract = Contract(
                publisher=source.publisher,
                valid_from=datetime.now(),
                open_source=source_form.cleaned_data['open_license'],
                state=contract_constants.CONTRACT_STATE_VALID
            )
            contract.save()
            contract.sources.add(source)

        for form in seed_formset.forms:
            seed = form.save(commit=False)
            if seed.url:  # prevent saving empty fields
                seed.source = source
                seed.save()

        return HttpResponseRedirect(source.get_absolute_url())


class SourceDetail(SourceView, DetailView, CommentViewGeneric, URLView):
    template_name = 'source.html'
    context_object_name = 'source'
    threaded_comments = True

    url = U / 'detail' / pk
    url_name = 'detail'


class SourceEdit(SourceView, generic_views.EditView, URLView):
    form_class = forms.SourceEditForm
    template_name = 'edit_source.html'

    url = U / 'edit' / pk
    url_name = 'edit'


class EditSeeds(SourceView, FormView, generic_views.ObjectMixinFixed, URLView):
    form_class = forms.EditFormset
    template_name = 'formset_verbose.html'
    title = _('Edit seeds')

    url = U / 'seeds' / pk
    url_name = 'edit_seeds'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super(EditSeeds, self).get_form_kwargs()
        kwargs['queryset'] = self.object.seed_set.all()
        return kwargs

    def form_valid(self, form):
        seeds = form.save(commit=False)
        for seed in seeds:
            if seed.url:
                seed.source = self.object
                seed.save()

        for obj in form.deleted_objects:
            obj.delete()

        return HttpResponseRedirect(self.get_success_url())


class History(SourceView, generic_views.HistoryView, URLView):
    """
        History log
    """
    url = U / 'history' / pk
    url_name = 'history'


class SourceList(SourceView, generic_views.FilteredListView, URLView):
    title = _('Sources')
    table_class = tables.SourceTable
    filter_class = field_filters.SourceFilter

    url = U / 'list'
    url_name = 'list'
