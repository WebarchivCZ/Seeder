import forms
import models
import tables
import field_filters
import constants

from django.views.generic import DetailView
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django_tables2 import SingleTableView
from formtools.wizard.views import SessionWizardView

from publishers.forms import PublisherForm
from datetime import datetime
from core.utils import LoginMixin
from comments.views import CommentViewGeneric


class AddSource(LoginMixin, SessionWizardView):
    template_name = 'add_source.html'
    title = _('Add source')
    view_name = 'add_source'

    form_list = [
        ('source', forms.SourceForm),
        ('publisher', PublisherForm),
        ('seeds', forms.SeedFormset),
    ]

    @staticmethod
    def show_publisher_form(wizard):
        """
            This will be called to decide whether publisher form
            should be shown or not...

            If user already filled out publisher in step `source`
            then step `publisher` should be skipped.
        """
        cleaned_data = wizard.get_cleaned_data_for_step('source') or {}
        return not cleaned_data.get('publisher', False)

    condition_dict = {
        'publisher': show_publisher_form
    }

    def get_form(self, step=None, data=None, files=None):
        """
            Dynamically set source form according to user rights
        """
        step = step or self.steps.current
        is_manager = self.request.user.has_perm('core.manage_sources')
        if step == 'source' and is_manager:
            form_class = self.form_list[step]
            return forms.ManagementSourceForm(
                data=data,
                files=files,
                prefix=self.get_form_prefix(step, form_class))
        return super(AddSource, self).get_form(step, data, files)

    def get_template_names(self):
        if self.steps.current == 'seeds':
            return 'add_seeds.html'
        return super(AddSource, self).get_template_names()

    def done(self, form_list, **kwargs):
        form_dict = kwargs['form_dict']
        user = self.request.user
        source_form = form_dict['source']
        publisher_form = form_dict['publisher']
        seed_formset = form_dict['seeds']
        is_manager = user.has_perm('core.manage_sources')

        source = source_form.save(commit=False)
        source.created_by = user

        if not is_manager or not source.created_by:
            source.owner = user

        if not source.publisher:
            new_publisher = publisher_form.save()
            source.publisher = new_publisher

        source.save()

        if source_form.cleaned_data['open_license']:
            contract = models.Contract(
                source=source,
                date_start=datetime.now(),
                contract_type=constants.CONTRACT_CREATIVE_COMMONS
            )
            contract.save()

        for form in seed_formset.forms:
            seed = form.save(commit=False)
            if seed.url:  # prevent saving empty fields
                seed.source = source
                seed.save()

        return HttpResponseRedirect(source.get_absolute_url())


class SourceDetail(LoginMixin, DetailView, CommentViewGeneric):
    template_name = 'source.html'
    view_name = 'sources'
    context_object_name = 'source'
    model = models.Source
    anonymous = False
    threaded_comments = True


class SourceList(LoginMixin, SingleTableView):
    model = models.Source
    template_name = 'source_list.html'
    title = _('Sources')
    context_object_name = 'sources'
    view_name = 'sources'
    table_class = tables.SourceTable
    filter_class = field_filters.SourceFilter
    table_pagination = {"per_page": 20}

    def get_table_data(self):
        queryset = super(SourceList, self).get_table_data()
        return self.filter_class(self.request.GET, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super(SourceList, self).get_context_data(**kwargs)
        context['filter'] = self.filter_class(data=self.request.GET)
        return context
